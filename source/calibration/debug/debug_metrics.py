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
        camera,  # Объект камеры
        save_path="yandex_comparison.html"
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
    # print(f"📐 Матрица поворота:\n{R}")

    # Подсчёт ошибок (в ENU)
    errors = [
        np.linalg.norm(
            # np.array(R @ predict) -
            np.array( predict) -
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

    # point_gps_predict = [enu_to_gps(*R @ point, lat0, lon0) for point in points_cam]
    point_gps_predict = [enu_to_gps(*point, lat0, lon0) for point in points_cam]

    # url =generate_yandex_maps_url(point_gps_predict)
    # print(f'URL YANDEX {url}')
    save_yandex_comparison_map_html(point_gps_ideal, point_gps_predict, save_path)
    return {
        "rotation_matrix": R,
        "errors": errors,
        "stats": stats,
        "point_gps_predict": point_gps_predict,
        "point_gps_ideal": point_gps_ideal,
    }


def save_yandex_comparison_map_html(point_gps_ideal, point_gps_predict, save_path):
    """
    Сохраняет HTML-файл с Яндекс.Картой, на которой отображаются:
    - Зелёные точки: идеальные GPS координаты
    - Синие точки: предсказанные GPS (после обратной проекции)
    - Красные линии: векторы ошибок
    """
    if len(point_gps_ideal) != len(point_gps_predict):
        raise ValueError("Количество точек должно совпадать")

    center_lat = sum(lat for lat, lon in point_gps_ideal) / len(point_gps_ideal)
    center_lon = sum(lon for lat, lon in point_gps_ideal) / len(point_gps_ideal)

    placemarks = ""
    polylines = ""

    for i, (ideal, pred) in enumerate(zip(point_gps_ideal, point_gps_predict)):
        lat1, lon1 = ideal
        lat2, lon2 = pred

        placemarks += f"""
        myMap.geoObjects.add(new ymaps.Placemark([{lat1}, {lon1}], {{
            balloonContent: "📍 Исходная точка {i + 1}",
            hintContent: "📍 Исходная точка {i + 1}"
        }}, {{
            preset: "islands#greenDotIcon"
        }}));

        myMap.geoObjects.add(new ymaps.Placemark([{lat2}, {lon2}], {{
            balloonContent: "🎯 Спроецированная точка {i + 1}",
            hintContent: "🎯 Спроецированная точка {i + 1}"
        }}, {{
            preset: "islands#blueDotIcon"
        }}));
        """

        polylines += f"""
        myMap.geoObjects.add(new ymaps.Polyline([
            [{lat1}, {lon1}],
            [{lat2}, {lon2}]
        ], {{
            hintContent: "Вектор ошибки"
        }}, {{
            strokeColor: "#FF0000",
            strokeWidth: 3,
            strokeOpacity: 0.7
        }}));
        """

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Сравнение GPS точек</title>
    <meta charset="utf-8" />
    <script src="https://api-maps.yandex.ru/2.1/?lang=ru_RU" type="text/javascript"></script>
</head>
<body>
<div id="map" style="width: 100%; height: 600px;"></div>
<script>
ymaps.ready(function () {{
    var myMap = new ymaps.Map("map", {{
        center: [{center_lat}, {center_lon}],
        zoom: 18
    }});

    {placemarks}

    {polylines}
}});
</script>
</body>
</html>"""

    with open(save_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ HTML-карта с точками и векторами ошибок сохранена в: {save_path}")
