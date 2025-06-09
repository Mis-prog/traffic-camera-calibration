import numpy as np
from pyproj import Geod
from core import PointND, Camera


def gps_to_enu(lat, lon, ref_lat, ref_lon):
    """
    Перевод GPS (широта, долгота) в локальные координаты ENU (в метрах)
    """
    geod = Geod(ellps="WGS84")

    # Вычисляем расстояние и азимут до точки
    azimuth, _, distance = geod.inv(ref_lon, ref_lat, lon, lat)

    # Преобразуем в координаты ENU
    east = distance * np.sin(np.deg2rad(azimuth))
    north = distance * np.cos(np.deg2rad(azimuth))

    return east, north


def enu_to_gps(east, north, ref_lat, ref_lon):
    """
    Преобразует локальные координаты ENU (в метрах)
    обратно в GPS-координаты (широта, долгота).

    Parameters:
    -----------
    east : float
        Смещение на восток (в метрах)
    north : float
        Смещение на север (в метрах)
    ref_lat : float
        Начальная широта (градусы)
    ref_lon : float
        Начальная долгота (градусы)

    Returns:
    --------
    lat : float
        Новая широта
    lon : float
        Новая долгота
    """
    geod = Geod(ellps="WGS84")

    # Вычисляем азимут и расстояние
    distance = np.hypot(east, north)
    azimuth = np.rad2deg(np.arctan2(east, north))

    # Прямая геодезическая задача
    lon, lat, _ = geod.fwd(ref_lon, ref_lat, azimuth, distance)

    return lat, lon


def compute_alignment_rotation(camera, image_point, gps0, gps1):
    """
    Вычисляет матрицу поворота, которая совмещает направление из камеры (через project_back)
    с направлением на основе двух GPS-точек.

    camera: объект камеры
    image_point: пиксель на изображении (u, v)
    gps0, gps1: (lat, lon) — задают направление в ENU

    Возвращает:
    - матрицу поворота 2×2 (numpy.array)
    - угол в радианах
    """
    v_scene_all = camera.project_back(PointND(image_point, add_weight=True)).get()[:2]
    v_scene = v_scene_all / np.linalg.norm(v_scene_all)

    v_enu_all = gps_to_enu(gps1[0], gps1[1], gps0[0], gps0[1])
    v_enu = v_enu_all / np.linalg.norm(v_enu_all)

    cos_theta = np.dot(v_scene, v_enu)
    sin_theta = v_scene[0] * v_enu[1] - v_scene[1] * v_enu[0]
    theta = np.arctan2(sin_theta, cos_theta)

    R = np.array([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta), np.cos(theta)]
    ])
    return R, theta
