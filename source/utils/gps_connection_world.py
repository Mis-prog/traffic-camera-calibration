import numpy as np
from pyproj import Geod


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
