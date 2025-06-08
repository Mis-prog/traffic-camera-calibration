import matplotlib.pyplot as plt

from source import CalibrationPipeline, Camera, VanishingPointCalibration, \
    RefineOptimizer, PointND
from source.calibration.utils import load_lines, load_lines_from_json, extract_direction_vectors_from_lines
from calibration.refine import residual_interline_distance, residual_parallel_group, \
    residual_reprojection_line
from calibration.debug import load_scene_gps, visualize_source

from vp_detection import VanishingPointEstimatorManual

# Разметка данных
# from utils.data_markup_tool import LineAnnotationTool
#
# line_tool = LineAnnotationTool("image/pattern_corrected_image.png","marked","dist_ between_line_4.json")
# line_tool.run()

import numpy as np

lines_vp1 = load_lines("marked/horizontal_lines.json")
lines_vp3 = load_lines("marked/vertical_lines.json")
#
vp1_manual = VanishingPointEstimatorManual().estimate(lines_vp1)
vp3_manual = VanishingPointEstimatorManual().estimate(lines_vp3)
#
vps_manual = np.array([vp1_manual, vp3_manual])
#
camera = Camera('image/pattern_corrected_image.png')
#
# image = camera.get_image()
#
# import matplotlib.pyplot as plt
# plt.imshow(image)
# plt.scatter(vps_manual[0, 0], vps_manual[0, 1], c='r', label='Точка схода для направления X')
# plt.scatter(vps_manual[1, 0], vps_manual[1, 1], c='b', label='Точка схода для направления Z')


# for (x1, y1), (x2, y2) in lines_vp1:
#     plt.plot([x1, x2], [y1, y2], color='red', linewidth=2)
#
# for (x1, y1), (x2, y2) in lines_vp3:
#     plt.plot([x1, x2], [y1, y2], color='blue', linewidth=2)
# plt.legend()
# plt.show()


vp_init = VanishingPointCalibration(camera, debug_save_path='image/vp.png')
#
vp_init.set_vanishing_points(vpX=vps_manual[0], vpZ=vps_manual[1])

data = {
    "dist_between_line_1": load_lines('marked/dist_ between_line_1.json'),
    "dist_between_line_2": load_lines('marked/dist_ between_line_2.json'),
    "dist_between_line_3": load_lines('marked/dist_ between_line_3.json'),
    "dist_between_line_4": load_lines('marked/dist_ between_line_4.json'),
}

resualds_blocks_first = [
    lambda cam, data: residual_interline_distance(cam, data, group="dist_between_line_1", expected=11.5),
    lambda cam, data: residual_interline_distance(cam, data, group="dist_between_line_2", expected=4),
    lambda cam, data: residual_interline_distance(cam, data, group="dist_between_line_3", expected=4),
    lambda cam, data: residual_interline_distance(cam, data, group="dist_between_line_4", expected=4),
]

refiner_first = RefineOptimizer(camera=camera,
                                residual_blocks=resualds_blocks_first,
                                mask=[0, 6],
                                bounds=([800, 5], [2000, 30]),
                                # debug_save_path='image/',
                                )

resualds_blocks_second = [
]

refiner_second = RefineOptimizer(camera=camera,
                                 residual_blocks=resualds_blocks_second,
                                 mask=[1, 2, 3],
                                 bounds=([-20, 40, -180], [-5, 60, -150]),
                                 )
pipeline = CalibrationPipeline([vp_init, refiner_first])
camera = pipeline.run(camera, data)


from scipy.spatial.transform import Rotation as R
from scipy.optimize import minimize
import numpy as np

# === LOSS-компоненты ===

def loss_vertical_alignment(omega, R0, K, lines_img):
    delta_R = R.from_rotvec(omega).as_matrix()
    R_corr = delta_R @ R0
    z_world = np.array([0, 0, 1])

    loss = 0.0
    for line_dir in lines_img:
        line_dir = line_dir / np.linalg.norm(line_dir)
        v_cam = R_corr @ z_world
        v_img = K @ v_cam
        v_img = v_img[:2] / v_img[2]
        v_img = v_img / np.linalg.norm(v_img)
        cos_theta = np.dot(v_img, line_dir)
        loss += 1 - cos_theta ** 2
    return loss

def loss_planar_alignment(omega, R0, K, planar_lines_img):
    delta_R = R.from_rotvec(omega).as_matrix()
    R_corr = delta_R @ R0
    K_inv = np.linalg.inv(K)

    total_loss = 0.0
    for line_dir in planar_lines_img:
        line_dir = line_dir / np.linalg.norm(line_dir)
        dir_img_h = np.array([line_dir[0], line_dir[1], 1.0])
        dir_cam = K_inv @ dir_img_h
        dir_cam = dir_cam / np.linalg.norm(dir_cam)
        dir_world = R_corr.T @ dir_cam
        z_component = dir_world[2]
        total_loss += z_component ** 2
    return total_loss

# === Общий функционал ===

def total_loss(omega, R0, K, verticals=None, planar_lines=None, weights=(1.0, 1.0, 10.0)):
    lambda_vert, lambda_planar, lambda_reg = weights
    loss = 0.0

    if verticals:
        loss += lambda_vert * loss_vertical_alignment(omega, R0, K, verticals)
    if planar_lines:
        loss += lambda_planar * loss_planar_alignment(omega, R0, K, planar_lines)

    loss += lambda_reg * np.sum(omega ** 2)
    return loss

# === Данные ===
K = camera.intrinsics.get()
params = camera.get_params()

angles = params[1:4]
R0 = R.from_euler('zyx', angles, degrees=True).as_matrix()

lines_vertical = extract_direction_vectors_from_lines(load_lines('marked/vertical_lines.json'))
lines_horison = extract_direction_vectors_from_lines(load_lines('marked/horizontal_lines.json'))

initial_omega = np.zeros(3)
res = minimize(
    total_loss,
    initial_omega,
    args=(R0, K, lines_vertical, lines_horison, (0.5, 1.0, 10.0)),
    method='BFGS'
)

omega_opt = res.x
R_opt = R.from_rotvec(omega_opt).as_matrix() @ R0
euler_opt = R.from_matrix(R_opt).as_euler('zyx', degrees=True)

print(omega_opt, euler_opt)

camera.extrinsics.set_rotation(euler_opt)

from calibration.debug import visualize_grid_debug, visualize_grid_gps_debug
point_start = PointND(camera.intrinsics.get_main_point(), add_weight=True)
visualize_grid_debug(camera, point_start ,grid_range=10)