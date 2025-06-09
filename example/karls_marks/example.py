import matplotlib.pyplot as plt

from source import CalibrationPipeline, Camera, VanishingPointCalibration, \
    RefineOptimizer, PointND
from source.calibration.utils import load_lines, load_lines_from_json, extract_direction_vectors_from_lines
from calibration.refine import residual_interline_distance, residual_line_length
from calibration.debug import load_scene_gps, visualize_source

from vp_detection import VanishingPointEstimatorManual

import numpy as np

lines_vp1 = load_lines("marked/horizontal_lines.json")
lines_vp3 = load_lines("marked/vertical_lines.json")

vp1_manual = VanishingPointEstimatorManual().estimate(lines_vp1)
vp3_manual = VanishingPointEstimatorManual().estimate(lines_vp3)

vps_manual = np.array([vp1_manual, vp3_manual])

camera = Camera('image/pattern_corrected_image.png')

vp_init = VanishingPointCalibration(camera, debug_save_path='image/vp.png')
vp_init.set_vanishing_points(vpX=vps_manual[0], vpZ=vps_manual[1])

from utils import AnnotationParser

annotation_parser = AnnotationParser("marked/data_full.json")

data = {
    "pedestrian crossing": annotation_parser.get_lines_by_class("pedestrian crossing"),
    "pedestrian crossing 2": annotation_parser.get_lines_by_class("pedestrian crossing 2"),
    "pedestrian crossing 3": annotation_parser.get_lines_by_class("pedestrian crossing 3"),
    "distance between line": annotation_parser.get_lines_by_class("distance between line"),
}

resualds_blocks_first = [
    lambda cam, data: residual_interline_distance(cam, data, group="pedestrian crossing", expected=4.2),
    lambda cam, data: residual_interline_distance(cam, data, group="pedestrian crossing 2", expected=4.2),
    lambda cam, data: residual_interline_distance(cam, data, group="pedestrian crossing 3", expected=4.2),
    lambda cam, data: residual_interline_distance(cam, data, group="distance between line", expected=3.5),
    lambda cam, data: residual_line_length(cam, data, group="pedestrian crossing", expected=24)
]

refiner_first = RefineOptimizer(camera=camera,
                                residual_blocks=resualds_blocks_first,
                                mask=[0, 6],
                                bounds=([700, 2000], [5, 30]),
                                debug_save_path='image/',
                                method="minimize",
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
lines_horison = extract_direction_vectors_from_lines(load_lines('marked/horizontal_lines_all.json'))


def scaled_loss(scaled_omega, *args):
    scale = 0.01
    omega = scaled_omega * scale
    return total_loss(omega, *args)


res = minimize(
    scaled_loss,
    np.zeros(3),
    args=(R0, K, lines_vertical, lines_horison, (1, 1, 100)),
    method='BFGS'
)

omega_opt = res.x * 0.01

R_opt = R.from_rotvec(omega_opt).as_matrix() @ R0
euler_opt = R.from_matrix(R_opt).as_euler('zyx', degrees=True)

# print(omega_opt, euler_opt)

camera.extrinsics.set_rotation(euler_opt)

print(*camera.get_params())

from calibration.debug import visualize_grid_debug, visualize_grid_gps_debug

point_start = PointND(camera.intrinsics.get_main_point(), add_weight=True)
visualize_grid_debug(camera, point_start, grid_range=10, grid_step=2, save_path="image/grid_second.png")

# from calibration.debug import visualize_vps_debug
# visualize_vps_debug(camera, show=True)


from calibration.utils import gps_to_enu, enu_to_gps


def generate_yandex_maps_url(points):
    base_url = "https://yandex.ru/maps/?pt="
    coords = ["{:.6f},{:.6f}".format(lon, lat) for lat, lon in points]
    return base_url + "~".join(coords)


# error = []
# for _point_gps, _point_gps_ideal in zip(point_gps, point_gps_ideal):
#     # print(_point_gps, _point_gps_ideal)
#     _point_enu = np.array(gps_to_enu(*_point_gps, lat0, lon0))
#     _point_enu_ideal = np.array(gps_to_enu(*_point_gps_ideal, lat0, lon0))
#     dist = np.linalg.norm(_point_enu_ideal - _point_enu)
#     error.append(dist)
#
# print(f"📊 Статистика ошибок (в метрах):")
# print(f"  ▸ Средняя ошибка:      {np.mean(error):.2f} м")
# print(f"  ▸ Стандартное отклонение: {np.std(error):.2f} м")
# print(f"  ▸ Минимальная ошибка:  {np.min(error):.2f} м")
# print(f"  ▸ Максимальная ошибка: {np.max(error):.2f} м")
# print(f"  ▸ Медианная ошибка:    {np.median(error):.2f} м")

def estimate_rotation_svd(points_cam, points_enu):
    """
    points_cam — Nx2 точки из камеры (в мировой системе XY)
    points_enu — Nx2 точки в ENU системе координат
    """
    A = np.array(points_cam)
    B = np.array(points_enu)

    # Центрируем точки
    A_mean = A.mean(axis=0)
    B_mean = B.mean(axis=0)
    A_centered = A - A_mean
    B_centered = B - B_mean

    # SVD для A.T @ B
    H = A_centered.T @ B_centered
    U, S, Vt = np.linalg.svd(H)
    R = Vt.T @ U.T

    # Проверка на отражение (детерминант должен быть +1)
    if np.linalg.det(R) < 0:
        Vt[1, :] *= -1
        R = Vt.T @ U.T

    return R


point_test_gps = annotation_parser.get_points_by_class("gps_test")

lat0, lon0 = 54.725383, 55.941031
point_gps_ideal = [(54.725194, 55.940845),
                   (54.725242, 55.940414),
                   (54.725295, 55.940380),
                   (54.725469, 55.940450),
                   (54.725567, 55.940570)
                   ]

points_cam = [camera.project_back(PointND(pt, add_weight=True)).get()[:2] for pt in point_test_gps]
points_enu = [gps_to_enu(lat, lon, lat0, lon0) for lat, lon in point_gps_ideal]

R = estimate_rotation_svd(points_cam, points_enu)

anchor_3D = camera.project_back(PointND(camera.intrinsics.get_main_point(), add_weight=True), plane_z=0)
anchor_x, anchor_y, anchor_z = anchor_3D.get()

from calibration.debug import set_grid_real

count, world_points = set_grid_real(anchor_x, anchor_y, 10, 2, 0)

point_gps = []
for point in world_points:
    _point_world = point.get()[:2]
    _point_enu = enu_to_gps(*R @ _point_world, lat0, lon0)
    point_gps.append(_point_enu)

url = generate_yandex_maps_url(point_gps)
print("Ссылка для просмотра в Яндекс.Картах:")
print(url)

point_gps_control = [enu_to_gps(*R @ pt, lat0, lon0) for pt in points_cam]

url = generate_yandex_maps_url(point_gps_control)
print("Ссылка для просмотра в Яндекс.Картах:")
print(url)
