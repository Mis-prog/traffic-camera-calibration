import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from pyproj import Proj, transform
import requests
from PIL import Image
from io import BytesIO

from core import Camera, PointND
from utils import enu_to_gps


def visualize_grid_debug(
        camera: Camera,
        point_start: PointND,
        grid_range: float = 10.0,  # диапазон в метрах от центра
        grid_step: float = 1.0,  # размер клетки
        arrow_len: float = 5.0,  # длина вектора "вверх"
        plane_z: float = 0.0,  # плоскость, на которую кладём сетку
        save_path=None
):
    image = camera.get_image()
    height, width = image.shape[:2]

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_title("Калибровочная сетка (1×1 м) в проекции")
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    plt.imshow(image)

    anchor_3D = camera.project_back(point_start, plane_z=plane_z)
    anchor_x, anchor_y, anchor_z = anchor_3D.get()

    # Считаем количество узлов в сетке
    count, world_points = set_grid_real(anchor_x, anchor_y, grid_range, grid_step, plane_z)

    for i in range(count):
        for j in range(count - 1):
            p1 = world_points[i * count + j]
            p2 = world_points[i * count + (j + 1)]
            p1_proj = camera.project_direct(p1).get()
            p2_proj = camera.project_direct(p2).get()
            ax.plot([p1_proj[0], p2_proj[0]], [p1_proj[1], p2_proj[1]], color='blue', linewidth=1)

    for j in range(count):
        for i in range(count - 1):
            p1 = world_points[i * count + j]
            p2 = world_points[(i + 1) * count + j]
            p1_proj = camera.project_direct(p1).get()
            p2_proj = camera.project_direct(p2).get()
            ax.plot([p1_proj[0], p2_proj[0]], [p1_proj[1], p2_proj[1]], color='blue', linewidth=1)

    def draw_arrow_from_3D(p3D):
        base = camera.project_direct(p3D).get()
        tip_point = PointND(p3D.get() + np.array([0, 0, arrow_len]))
        tip = camera.project_direct(tip_point).get()

        # красная точка — основание
        ax.scatter(base[0], base[1], color='red', s=10, zorder=3)

        # чёрная стрелка — вверх
        ax.annotate(
            '', xy=(tip[0], tip[1]), xytext=(base[0], base[1]),
            arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
            annotation_clip=False, label=f'Высота: {arrow_len}'
        )

    top_left = world_points[0]
    top_right = world_points[count - 1]
    bottom_left = world_points[(count - 1) * count]
    bottom_right = world_points[-1]

    for corner in [top_left, top_right, bottom_left, bottom_right]:
        draw_arrow_from_3D(corner)

    draw_coordinate_system_overlay(camera, ax, scale=10)

    arrow_legend = mlines.Line2D([], [], color='black', marker=r'$\uparrow$', linestyle='None',
                                 markersize=10, label=f'Вектор вверх ({arrow_len} м)')

    ax.legend(handles=[arrow_legend])

    if save_path is not None:
        plt.savefig(save_path)
    plt.show()


def set_grid_real(anchor_x, anchor_y, grid_range, grid_step, plane_z):
    count = int(2 * grid_range / grid_step) + 1
    world_points = []
    for i in range(count):
        for j in range(count):
            x = anchor_x - grid_range + i * grid_step
            y = anchor_y - grid_range + j * grid_step
            world_points.append(PointND(np.array([x, y, plane_z])))
    return count, world_points


def draw_coordinate_system_overlay(camera: Camera, ax, scale=10):
    origin = PointND([0, 0, 0, 1])
    X = PointND([scale, 0, 0, 1])
    Y = PointND([0, scale, 0, 1])
    Z = PointND([0, 0, scale, 1])

    p0 = camera.project_direct(origin).get()
    print(f'Пиксель мировой системы координат: {p0}')
    px = camera.project_direct(X).get()
    py = camera.project_direct(Y).get()
    pz = camera.project_direct(Z).get()

    def draw_arrow(p_start, p_end, color, label):
        ax.annotate('', xy=p_end[:2], xytext=p_start[:2],
                    arrowprops=dict(arrowstyle='->', linewidth=2, color=color))
        ax.text(p_end[0], p_end[1], label, color=color,
                fontsize=12, fontweight='bold', ha='center', va='center')

    draw_arrow(p0, px, 'red', 'X')
    draw_arrow(p0, py, 'green', 'Y')
    draw_arrow(p0, pz, 'blue', 'Z')


def visualize_coordinate_system(camera: Camera, save_path: str):
    image = camera.get_image()
    scale = 10  # длина осей в условных единицах

    # Точки в мировой системе координат
    origin = PointND([0, 0, 0, 1])
    X = PointND([scale, 0, 0, 1])
    Y = PointND([0, scale, 0, 1])
    Z = PointND([0, 0, scale, 1])

    # Проекция на изображение
    p0 = camera.project_direct(origin).get()
    px = camera.project_direct(X).get()
    py = camera.project_direct(Y).get()
    pz = camera.project_direct(Z).get()

    # Отрисовка через matplotlib
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(image)
    ax.axis('off')

    def draw_arrow(p_start, p_end, color, label):
        ax.annotate(
            '', xy=p_end[:2], xytext=p_start[:2],
            arrowprops=dict(arrowstyle='->', linewidth=2, color=color)
        )
        ax.text(p_end[0], p_end[1], label, color=color,
                fontsize=12, fontweight='bold', ha='center', va='center')

    draw_arrow(p0, px, 'red', 'X')
    draw_arrow(p0, py, 'green', 'Y')
    draw_arrow(p0, pz, 'blue', 'Z')

    plt.savefig(save_path, bbox_inches='tight', pad_inches=0)


def load_scene_gps(lon, lat, save_path=None, zoom=19, size=(650, 450)):
    # Скачиваем изображение
    url = f"https://static-maps.yandex.ru/1.x/?ll={lon},{lat}&z={zoom}&l=sat&size={size[0]},{size[1]}"
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))

    if save_path is not None:
        image.save(save_path)

    return image


# todo передалать
def gps_to_pixel(lat, lon, ref_lat, ref_lon, img_width, img_height, meters_per_pixel=0.3):
    """
    Преобразует GPS в пиксели, предполагая, что ref_lat/lon находится в центре.
    """
    from pyproj import Geod
    geod = Geod(ellps="WGS84")

    def meters_per_pixel(zoom, lat):
        return 156543.03392 * np.cos(np.deg2rad(lat)) / (2 ** zoom)

    # Смещение на восток и север (в метрах)
    az_east, _, east = geod.inv(ref_lon, ref_lat, lon, ref_lat)
    az_north, _, north = geod.inv(ref_lon, ref_lat, ref_lon, lat)

    if lat < ref_lat:
        north = -north
    if lon < ref_lon:
        east = -east

    x = img_width / 2 + east / meters_per_pixel
    y = img_height / 2 - north / meters_per_pixel  # сверху вниз

    return x, y


def visualize_grid_gps_debug(
        camera: Camera,
        point_start: PointND,
        gps_origin: tuple,
        grid_range: float = 10.0,  # диапазон в метрах от центра
        grid_step: float = 1.0,  # размер клетки
        plane_z: float = 0.0,  # плоскость, на которую кладём сетку
        save_path=None
):
    ref_lat, ref_lon = gps_origin

    image = load_scene_gps(ref_lon, ref_lat, zoom=19)
    image_np = np.array(image)
    height, width = image_np.shape[:2]

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(image_np)
    ax.set_title("ENU-сетка на спутнике")

    anchor_3D = camera.project_back(point_start, plane_z=plane_z)
    anchor_x, anchor_y, anchor_z = anchor_3D.get()

    count, world_points = set_grid_real(anchor_x, anchor_y, grid_range, grid_step, plane_z)  # enu

    for i in range(count):
        for j in range(count - 1):
            world_point_1 = world_points[i * count + j]
            world_point_2 = world_points[i * count + j + 1]
            east1, north1 = world_point_1.get()[:2]
            east2, north2 = world_point_2.get()[:2]

            lat1, lon1 = enu_to_gps(east1, north1, ref_lat, ref_lon)
            lat2, lon2 = enu_to_gps(east2, north2, ref_lat, ref_lon)
            px1, py1 = gps_to_pixel(lat1, lon1, ref_lat, ref_lon, width, height)
            px2, py2 = gps_to_pixel(lat2, lon2, ref_lat, ref_lon, width, height)

            ax.plot([px1, px2], [py1, py2], color='red')

    for j in range(count):
        for i in range(count - 1):
            world_point_1 = world_points[i * count + j]
            world_point_2 = world_points[(i + 1) * count + j]
            east1, north1 = world_point_1.get()[:2]
            east2, north2 = world_point_2.get()[:2]

            lat1, lon1 = enu_to_gps(east1, north1, ref_lat, ref_lon)
            lat2, lon2 = enu_to_gps(east2, north2, ref_lat, ref_lon)
            px1, py1 = gps_to_pixel(lat1, lon1, ref_lat, ref_lon, width, height)
            px2, py2 = gps_to_pixel(lat2, lon2, ref_lat, ref_lon, width, height)

            ax.plot([px1, px2], [py1, py2], color='red')

    plt.show()
