import numpy as np
from source.calibration.utils import gps_to_enu, enu_to_gps
from source.core import PointND


def generate_yandex_maps_url(points):
    base_url = "https://yandex.ru/maps/?pt="
    coords = ["{:.6f},{:.6f}".format(lon, lat) for lat, lon in points]
    return base_url + "~".join(coords)


# Вращение от мира к gps через SVD
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


def compute_alignment_and_metrics(
        point_image,  # Точки с изображения
        point_gps_ideal,  # Идеальные GPS точки
        lat0, lon0,  # Начальная точка ENU-системы
        camera  # Объект камеры
):
    # Обратная проекция GPS в мировую систему (XY)
    points_cam = [
        camera.project_back(PointND(pt, add_weight=True)).get()[:2]
        for pt in point_image
    ]

    # Идеальные GPS → ENU
    points_enu = [
        gps_to_enu(lat, lon, lat0, lon0)
        for lat, lon in point_gps_ideal
    ]

    # Поворот между камерами и ENU
    R = estimate_rotation_svd(points_cam, points_enu)
    print(f"📐 Матрица поворота:\n{R}")

    # Подсчёт ошибок (в ENU)
    errors = [
        np.linalg.norm(
            np.array(R @ predict) -
            np.array(ideal)
        )
        for predict, ideal in zip(points_cam, points_enu)
    ]

    stats = {
        "Средняя ошибка": np.mean(errors),
        "Стандартное отклонение": np.std(errors),
        "Минимальная ошибка": np.min(errors),
        "Максимальная ошибка": np.max(errors),
        "Медианная ошибка": np.median(errors),
    }

    print("\n📊 Статистика ошибок (в метрах):")
    for name, value in stats.items():
        print(f"  ▸ {name:<24} {value:.2f} м")

    point_gps_predict = [enu_to_gps(*R @ point, lat0, lon0) for point in points_cam]

    url =generate_yandex_maps_url(point_gps_predict)
    print(f'URL YANDEX {url}')
    return {
        "rotation_matrix": R,
        "errors": errors,
        "stats": stats,
    }
