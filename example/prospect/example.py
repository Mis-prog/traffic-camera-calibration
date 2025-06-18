import numpy as np
import matplotlib.pyplot as plt

from source import CalibrationPipeline, Camera, VanishingPointCalibration, \
    RefineOptimizer, PointND
from source.calibration.utils import load_lines, load_lines_from_json, extract_direction_vectors_from_lines
from source.calibration.refine import residual_interline_distance, residual_line_length, residual_reprojection_line, \
    residual_vertical_alignment, residual_planar_alignment, residual_alignment_block, get_plane_normal
from source.calibration.debug import load_scene_gps, visualize_source, generate_yandex_maps_url, \
    compute_alignment_and_metrics
from source.vp_detection import VanishingPointEstimatorManual
from source.calibration.utils import gps_to_enu, enu_to_gps
from source.annotation_tools import AnnotationParser
from calibration.debug import load_scene_gps, visualize_source, projection_line

annotation_parser = AnnotationParser("data/data_full.json")

lines_vp1 = annotation_parser.get_lines_by_class("vp1")
lines_vp3 = annotation_parser.get_lines_by_class("vp3")
vp1_manual = VanishingPointEstimatorManual().estimate(lines_vp1)
vp3_manual = VanishingPointEstimatorManual().estimate(lines_vp3)

# print(f'vp1: {vp1_manual}, vp3: {vp3_manual}')

camera = Camera('data/pattern_corrected_image.png')

# plt.imshow(camera.get_image())
# plt.scatter(*vp1_manual, color='r')
# # plt.scatter(*vp3_manual, color='g')
# plt.show()

vp_init = VanishingPointCalibration(camera, debug_save_path='data/vp.png')
vp_init.set_vanishing_points(vpX=vp1_manual, vpZ=vp3_manual)


def back_refine(camera, not_init=True):
    global data
    data = {
        "Расстояние между линиями": annotation_parser.get_lines_by_class("vp1"),
    }
    resualds_blocks_first = [
        lambda cam, data: residual_interline_distance(cam, data, group="Расстояние между линиями", expected=3.4),
    ]

    global refiner_1
    refiner_1 = RefineOptimizer(
        camera=camera,
        residual_blocks=resualds_blocks_first,
        mask=[6],
        bounds=[[14], [60]],
        debug_save_path='data/grid_back_1.png',
        method="trf",
        grid_range=(15, 15),
        point_start=[1920 / 2 - 360, 1080 / 2 - 100]
    )

    refiner_2 = RefineOptimizer(
        camera=camera,
        residual_blocks=resualds_blocks_first,
        mask=[0, 6],
        bounds=[[1000, 14], [2000, 60]],
        debug_save_path='data/grid_back_1.png',
        method="trf",
        grid_range=(15, 15),
        point_start=[1920 / 2 + 100, 1080 / 2 + 270]
    )

    pipeline = CalibrationPipeline(
        init_stage=vp_init,
        refine_stages=[refiner_1, refiner_2],
        n_iter=1
    )

    camera = pipeline.run(camera, data)

    return camera


camera = back_refine(camera)

# from scipy.spatial.transform import Rotation
# from scipy.optimize import minimize
#
#
# def optimize_pitch_yaw_loss(angles_xy_deg, camera, lines_on_ground):
#     alpha_deg, beta_deg = angles_xy_deg
#     alpha_rad = np.deg2rad(alpha_deg)
#     beta_rad = np.deg2rad(beta_deg)
#
#     R0 = camera.extrinsics.get_rotation()
#
#     # Локальные оси камеры
#     x_cam = R0[:, 0]
#     y_cam = R0[:, 1]
#
#     # Вращение вокруг X и Y осей (в мировой системе)
#     R_x = Rotation.from_rotvec(alpha_rad * x_cam).as_matrix()
#     R_y = Rotation.from_rotvec(beta_rad * y_cam).as_matrix()
#
#     R_delta = R_y @ R_x  # сначала вокруг X, потом вокруг Y
#     R_new = R0 @ R_delta
#
#     camera.extrinsics.set_rotation(R_new,from_type='vp')
#
#     # Оцениваем ошибку: нормали от горизонтальных линий должны быть вертикальны
#     errors = []
#     n_target = np.array([0, 0, 1])
#
#     for p1, p2 in lines_on_ground:
#         n = get_plane_normal(camera, p1, p2)  # нормаль в мировой СК
#         angle = np.arccos(np.clip(np.dot(n, n_target), -1, 1))
#         errors.append(angle ** 2)
#
#     return np.mean(errors)
#
# lines_on_ground = annotation_parser.get_lines_by_class("Горизонтальные линии")
#
# res = minimize(
#     lambda a: optimize_pitch_yaw_loss(a, camera, lines_on_ground),
#     x0=[0.0, 0.0],
#     bounds=[(-5, 5), (-5, 5)],
#     method='L-BFGS-B',
#     options={'ftol': 1e-9}
# )
#
# print("Оптимальные углы (deg):", res.x)
#
# R_final = camera.extrinsics.get_angles()
# print("Итоговая матрица вращения:\n", R_final)
#
# #
# from source.calibration.debug import visualize_grid_debug, visualize_grid_gps_debug
#
# camera.extrinsics.set_rotation([-59.49, 60, 176.92])
#
# point_start = PointND(refiner_1.point_start, add_weight=True)
# visualize_grid_debug(camera, point_start, save_path='data/grid_back_1_refine.png', grid_range_x=15, grid_range_y=15,
#                      grid_step=1)
