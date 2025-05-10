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