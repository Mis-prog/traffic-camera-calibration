import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import Axes3D

# === Параметры сцены ===
road_width = 8  # Ширина каждой полосы
intersection_size = 20  # Размер перекрестка
building_width = 15
building_height_left = 25
building_height_right = 30
traffic_light_height = 0
pole_height = 8

shift_x = 30
shift_y = road_width + 20


def shift_point(p):
    return [p[0] + shift_x, p[1] + shift_y, p[2]]


def shift_geometry(geom):
    return [shift_point(p) for p in geom]


def shift_object(obj):
    return {
        "type": obj["type"],
        "geometry": shift_geometry(obj["geometry"])
    }


# === Создание перекрестка (две пересекающиеся дороги) ===
def create_intersection():
    """Создает основной перекресток"""
    roads = []

    # Главная дорога (горизонтальная)
    main_road = {
        "type": "road_main",
        "geometry": [
            [-40, -road_width, 0], [70, -road_width, 0],
            [70, road_width, 0], [-40, road_width, 0]
        ]
    }

    # Удлинённая пересекающая дорога (вертикальная)
    cross_road = {
        "type": "road_cross",
        "geometry": [
            [-road_width, -40, 0], [road_width, -40, 0],
            [road_width, 60, 0], [-road_width, 60, 0]
        ]
    }

    return [shift_object(main_road), shift_object(cross_road)]


# === Разметка дорог ===
def create_lane_markings():
    """Создает разметку полос движения - 3 белые линии на каждую дорогу"""
    markings = []
    full_lane = []

    # Разметка для горизонтальной дороги (3 линии)
    y_positions = [-road_width / 2, 0, road_width / 2]  # 3 линии разметки
    for y_pos in y_positions:
        for x in np.arange(-40, 70, 6):
            if abs(x) > road_width + 2:  # Не рисуем разметку в зоне перекрестка
                markings.append({
                    "type": "lane_marking",
                    "geometry": [[x, y_pos, 0.02], [x + 3, y_pos, 0.02]]
                })

    for y_pos in y_positions:
        full_lane.append([shift_point([-20, y_pos, 0]), shift_point([20, y_pos, 0])])

    y_positions = [-road_width / 2, 0, road_width / 2]

    # Разметка для вертикальной дороги (3 линии)
    x_positions = [-road_width / 2, 0, road_width / 2]  # 3 линии разметки
    for x_pos in x_positions:
        for y in np.arange(-40, 60, 6):
            if abs(y) > road_width + 2:  # Не рисуем разметку в зоне перекрестка
                markings.append({
                    "type": "lane_marking",
                    "geometry": [[x_pos, y, 0.02], [x_pos, y + 3, 0.02]]
                })

    for x_pos in x_positions:
        full_lane.append([shift_point([x_pos, -20, 0]), shift_point([x_pos, 20, 0])])

    return [shift_object(obj) for obj in markings], full_lane


# === Пешеходные переходы ===
def create_crosswalks():
    """Создает пешеходные переходы в границах проезжей части"""
    crosswalks = []
    stripe_width = 1.0
    crosswalk_width = 4.0  # ширина перехода (по направлению движения)

    road_span = 2 * road_width
    num_stripes = int(road_span // 1.5)
    start_x = -road_width + (road_span - num_stripes * 1.5) / 2  # центрируем
    start_y = -road_width + (road_span - num_stripes * 1.5) / 2

    # Горизонтальные переходы (верх и низ перекрестка)
    for y_side in [-road_width - crosswalk_width / 2, road_width + crosswalk_width / 2]:
        for i in range(num_stripes):
            x_start = start_x + i * 1.5
            crosswalks.append({
                "type": "crosswalk",
                "geometry": [
                    [x_start, y_side - crosswalk_width / 2, 0.01],
                    [x_start + stripe_width, y_side - crosswalk_width / 2, 0.01],
                    [x_start + stripe_width, y_side + crosswalk_width / 2, 0.01],
                    [x_start, y_side + crosswalk_width / 2, 0.01]
                ]
            })

    # Вертикальные переходы (лево и право перекрестка)
    for x_side in [-road_width - crosswalk_width / 2, road_width + crosswalk_width / 2]:
        for i in range(num_stripes):
            y_start = start_y + i * 1.5
            crosswalks.append({
                "type": "crosswalk",
                "geometry": [
                    [x_side - crosswalk_width / 2, y_start, 0.01],
                    [x_side + crosswalk_width / 2, y_start, 0.01],
                    [x_side + crosswalk_width / 2, y_start + stripe_width, 0.01],
                    [x_side - crosswalk_width / 2, y_start + stripe_width, 0.01]
                ]
            })

    return [shift_object(obj) for obj in crosswalks]


# === Фонарные столбы и светофоры ===
def create_traffic_infrastructure():
    """Создает больше фонарных столбов и светофоров вокруг перекрестка"""
    poles = []
    traffic_lights = []

    # Основные позиции столбов на углах перекрестка
    main_pole_positions = [
        [-road_width - 4, -road_width - 4],
        [road_width + 4, -road_width - 4],
        [road_width + 4, road_width + 4],
        [-road_width - 4, road_width + 4]
    ]

    # Дополнительные столбы вдоль дорог
    additional_pole_positions = [
        [-25, -road_width - 4],
        [25, -road_width - 4],
        [-25, road_width + 4],
        # [25, road_width + 4],
        [-road_width - 4, -20],
        [-road_width - 4, 20],
        [road_width + 4, -20],
        [road_width + 4, 20]
    ]

    all_positions = main_pole_positions + additional_pole_positions

    for i, (x, y) in enumerate(all_positions):
        # Столб
        poles.append({
            "type": "pole",
            "geometry": [[x, y, 0], [x, y, pole_height]]
        })

        # Светофоры только на основных позициях (углы перекрестка)
        if i < 4:  # Первые 4 позиции - основные
            traffic_lights.append({
                "type": "traffic_light",
                "geometry": [
                    [x - 0.3, y - 0.3, pole_height],
                    [x + 0.3, y - 0.3, pole_height],
                    [x + 0.3, y + 0.3, pole_height],
                    [x - 0.3, y + 0.3, pole_height],
                    [x - 0.3, y - 0.3, pole_height + traffic_light_height],
                    [x + 0.3, y - 0.3, pole_height + traffic_light_height],
                    [x + 0.3, y + 0.3, pole_height + traffic_light_height],
                    [x - 0.3, y + 0.3, pole_height + traffic_light_height]
                ]
            })

    poles_shifted = [shift_object(p) for p in poles]
    lights_shifted = [shift_object(l) for l in traffic_lights]
    return poles_shifted, lights_shifted


# === Здания ===
def create_buildings():
    """Создает два здания по краям сцены"""
    buildings = []

    # Здание слева
    # buildings.append({
    #     "type": "building",
    #     "geometry": [
    #         [-50, -25, 0], [-20, -25, 0], [-20, -road_width - 3, 0], [-50, -road_width - 3, 0],
    #         [-50, -25, building_height_left], [-20, -25, building_height_left],
    #         [-20, -road_width - 3, building_height_left], [-50, -road_width - 3, building_height_left]
    #     ]
    # })

    # Здание справа
    buildings.append({
        "type": "building",
        "geometry": [
            [20, road_width + 3, 0], [50, road_width + 3, 0], [50, 25, 0], [20, 25, 0],
            [20, road_width + 3, building_height_right], [50, road_width + 3, building_height_right],
            [50, 25, building_height_right], [20, 25, building_height_right]
        ]
    })

    return [shift_object(obj) for obj in buildings]


# === Системы координат ===
def draw_coordinate_systems(ax):
    """Рисует мировую систему координат на краю здания и систему координат камеры"""

    # Мировая система координат (на краю левого здания)
    world_origin = [0, 0, 0]  # Край левого здания
    axis_length = 8

    # X-axis (красный)
    ax.plot([world_origin[0], world_origin[0] + axis_length],
            [world_origin[1], world_origin[1]],
            [world_origin[2], world_origin[2]], 'r-', linewidth=4, label='World X')

    # Y-axis (зеленый)
    ax.plot([world_origin[0], world_origin[0]],
            [world_origin[1], world_origin[1] + axis_length],
            [world_origin[2], world_origin[2]], 'g-', linewidth=4, label='World Y')

    # Z-axis (синий)
    ax.plot([world_origin[0], world_origin[0]],
            [world_origin[1], world_origin[1]],
            [world_origin[2], world_origin[2] + axis_length], 'b-', linewidth=4, label='World Z')

    # Система координат камеры (над мировой системой координат)

    from scipy.spatial.transform import Rotation

    R = Rotation.from_euler('zxy', [-142.28, 49.46, 172.08], degrees=True).as_matrix()

    # Позиция камеры над мировой системой координат
    camera_origin = [world_origin[0], world_origin[1], world_origin[2] + 25]
    camera_axis_length = 4

    # Базовые векторы осей камеры
    x_axis = np.array([camera_axis_length, 0, 0])
    y_axis = np.array([0, camera_axis_length, 0])
    z_axis = np.array([0, 0, camera_axis_length])

    # Поворачиваем оси согласно углам Тейта-Брайана
    x_axis_rot = R.T @ x_axis
    y_axis_rot = R.T @ y_axis
    z_axis_rot = R.T @ z_axis

    # Camera X-axis (темно-красный)
    ax.plot([camera_origin[0], camera_origin[0] + x_axis_rot[0]],
            [camera_origin[1], camera_origin[1] + x_axis_rot[1]],
            [camera_origin[2], camera_origin[2] + x_axis_rot[2]],
            color='darkred', linewidth=3, linestyle='--', label='Camera X')

    # Camera Y-axis (темно-зеленый)
    ax.plot([camera_origin[0], camera_origin[0] + y_axis_rot[0]],
            [camera_origin[1], camera_origin[1] + y_axis_rot[1]],
            [camera_origin[2], camera_origin[2] + y_axis_rot[2]],
            color='darkgreen', linewidth=3, linestyle='--', label='Camera Y')

    # Camera Z-axis (темно-синий)
    ax.plot([camera_origin[0], camera_origin[0] + z_axis_rot[0]],
            [camera_origin[1], camera_origin[1] + z_axis_rot[1]],
            [camera_origin[2], camera_origin[2] + z_axis_rot[2]],
            color='darkblue', linewidth=3, linestyle='--', label='Camera Z')

    # Подписи осей
    ax.text(world_origin[0] + axis_length + 1, world_origin[1], world_origin[2],
            'X_world', fontsize=12, color='red', weight='bold')
    ax.text(world_origin[0], world_origin[1] + axis_length + 1, world_origin[2],
            'Y_world', fontsize=12, color='green', weight='bold')
    ax.text(world_origin[0], world_origin[1], world_origin[2] + axis_length + 1,
            'Z_world', fontsize=12, color='blue', weight='bold')

    ax.text(camera_origin[0] + x_axis_rot[0] + 0.5, camera_origin[1] + x_axis_rot[1],
            camera_origin[2] + x_axis_rot[2], 'X_cam', fontsize=10, color='darkred', weight='bold')
    ax.text(camera_origin[0] + y_axis_rot[0], camera_origin[1] + y_axis_rot[1] + 0.5,
            camera_origin[2] + y_axis_rot[2], 'Y_cam', fontsize=10, color='darkgreen', weight='bold')
    ax.text(camera_origin[0] + z_axis_rot[0], camera_origin[1] + z_axis_rot[1],
            camera_origin[2] + z_axis_rot[2] + 0.5, 'Z_cam', fontsize=10, color='darkblue', weight='bold')


# === Создание сцены ===
# Создаем все объекты
roads = create_intersection()
lane_markings, full_lane_markings = create_lane_markings()
crosswalks = create_crosswalks()
poles, traffic_lights = create_traffic_infrastructure()
buildings = create_buildings()

# Объединяем все объекты
scene_objects = roads + lane_markings + crosswalks + poles + traffic_lights + buildings

# === Визуализация ===
fig = plt.figure(figsize=(16, 12))
ax = fig.add_subplot(111, projection='3d')

# Настройка заголовка и осей
ax.set_title("Сцена дорожного движения с перекрестком\n(с мировой системой координат и системой координат камеры)",
             fontsize=14, pad=20)
ax.set_xlabel("X (м)", fontsize=12)
ax.set_ylabel("Y (м)", fontsize=12)
ax.set_zlabel("Z (м)", fontsize=12)

# Отрисовка всех объектов сцены
for obj in scene_objects:
    obj_type = obj["type"]
    geometry = obj["geometry"]

    if obj_type in ["road_main", "road_cross"]:
        # Дороги как плоские полигоны
        verts = [geometry]
        ax.add_collection3d(Poly3DCollection(verts, facecolor='darkgray', alpha=0.8, edgecolor='black'))

    elif obj_type == "building":
        # Здания как 3D параллелепипеды
        verts = [
            [geometry[i] for i in [0, 1, 2, 3]],  # Нижняя грань
            [geometry[i] for i in [4, 5, 6, 7]],  # Верхняя грань
            [geometry[i] for i in [0, 1, 5, 4]],  # Боковые грани
            [geometry[i] for i in [1, 2, 6, 5]],
            [geometry[i] for i in [2, 3, 7, 6]],
            [geometry[i] for i in [3, 0, 4, 7]]
        ]
        ax.add_collection3d(Poly3DCollection(verts, facecolor='lightblue', alpha=0.7, edgecolor='navy'))

    elif obj_type == "traffic_light":
        # Светофоры как 3D коробки
        verts = [
            [geometry[i] for i in [0, 1, 2, 3]],  # Нижняя грань
            [geometry[i] for i in [4, 5, 6, 7]],  # Верхняя грань
            [geometry[i] for i in [0, 1, 5, 4]],  # Боковые грани
            [geometry[i] for i in [1, 2, 6, 5]],
            [geometry[i] for i in [2, 3, 7, 6]],
            [geometry[i] for i in [3, 0, 4, 7]]
        ]
        ax.add_collection3d(Poly3DCollection(verts, facecolor='red', alpha=0.9, edgecolor='darkred'))

    elif obj_type == "crosswalk":
        # Пешеходные переходы как белые полосы
        verts = [geometry]
        ax.add_collection3d(Poly3DCollection(verts, facecolor='white', alpha=0.9, edgecolor='black'))

    else:
        # Линейные объекты (столбы, разметка)
        if len(geometry) >= 2:
            xs, ys, zs = zip(*geometry)
            color_map = {
                "lane_marking": 'white',
                "pole": 'black'
            }
            color = color_map.get(obj_type, 'blue')
            linewidth = 4 if obj_type == "pole" else 3
            ax.plot(xs, ys, zs, color=color, linewidth=linewidth)

# Рисуем системы координат
draw_coordinate_systems(ax)

# # Настройка вида
# ax.set_xlim(-50, 50)
# ax.set_ylim(-35, 35)
# ax.set_zlim(0, 35)

# Улучшенный угол обзора
ax.view_init(elev=25, azim=45)

# Добавляем легенду для систем координат
ax.legend(loc='upper left', bbox_to_anchor=(0, 1))

# Улучшаем внешний вид
plt.tight_layout()


# plt.show()

def project_building_faces(building_geometry, camera):
    """
    Проецирует здание как набор отдельных граней
    building_geometry: 8 точек параллелепипеда [x,y,z]
    camera: объект камеры с методом project_direct
    """
    # Определяем грани здания (каждая грань - 4 точки)
    # Нумерация точек: 0-3 нижние, 4-7 верхние
    faces = [
        [0, 1, 2, 3],  # Нижняя грань (основание)
        [4, 5, 6, 7],  # Верхняя грань (крыша)
        [0, 1, 5, 4],  # Передняя грань
        [1, 2, 6, 5],  # Правая грань
        [2, 3, 7, 6],  # Задняя грань
        [3, 0, 4, 7]  # Левая грань
    ]

    projected_faces = []

    for face_indices in faces:
        # Получаем точки грани
        face_points = [building_geometry[i] for i in face_indices]

        # Проецируем каждую точку
        projected_points = []
        for pt in face_points:
            pt_proj = camera.project_direct(PointND(pt, add_weight=True)).get()
            projected_points.append(pt_proj)

        projected_faces.append(np.array(projected_points))

    return projected_faces


def draw_building_with_faces(ax, building_obj, camera, color='lightblue'):
    """
    Отрисовывает здание с правильным разделением на грани
    """
    geometry = building_obj['geometry']
    projected_faces = project_building_faces(geometry, camera)

    # Отрисовываем каждую грань отдельно
    for i, face in enumerate(projected_faces):
        if len(face) >= 3:  # Проверяем что грань имеет достаточно точек
            # Можем варьировать прозрачность для разных граней
            alpha = 0.6 if i < 2 else 0.8  # Верх/низ более прозрачные
            ax.fill(face[:, 0], face[:, 1], color=color, alpha=alpha, edgecolor='navy', linewidth=1)


print("Сцена создана успешно!")
print("Компоненты сцены:")
print("- Перекресток с двумя пересекающимися дорогами")
print("- Белая разметка полос движения (по 3 линии на каждую дорогу)")
print("- Широкие пешеходные переходы (4м) на всех четырех сторонах")
print("- 12 фонарных столбов (4 со светофорами на углах + 8 дополнительных)")
print("- Два здания по краям сцены")
print("- Мировая система координат (на краю левого здания)")
print("- Система координат камеры (над мировой системой, углы Тейта-Брайана)")

from source.core import Camera, PointND

camera = Camera(size=(1080, 1920))
camera.set_params_from_list([1200, -150, 55, 175, 0, 0, 25])

print(f'Исходные координаты{[1200, -150, 55, 175, 0, 0, 25]}')

fig, ax = plt.subplots(figsize=(12, 9))

# Цвета по типу объектов
color_map = {
    'road_main': 'darkgray',
    'road_cross': 'darkgray',
    'building': 'lightblue',
    'crosswalk': 'white',
    'traffic_light': 'red',
    'pole': 'black',
    'lane_marking': 'white'
}

# Отрисовка
for obj in scene_objects:
    color = color_map.get(obj['type'], 'green')
    geometry = obj['geometry']

    if obj['type'] == 'building':
        # Специальная обработка для зданий
        draw_building_with_faces(ax, obj, camera, color)
    else:
        # Обычная обработка для других объектов
        projected = []
        for pt in geometry:
            pt_proj = camera.project_direct(PointND(pt, add_weight=True)).get()
            projected.append(pt_proj)

        projected = np.array(projected)

        if obj['type'] in ['road_main', 'road_cross', 'crosswalk', 'traffic_light']:
            if len(projected) >= 3:
                ax.fill(projected[:, 0], projected[:, 1], color=color, alpha=0.8)
        else:
            if len(projected) == 2:
                ax.plot(projected[:, 0], projected[:, 1], color=color, linewidth=2)

# plt.tight_layout()
# plt.show()

import numpy as np


def get_direction(p1, p2):
    v = np.array(p2) - np.array(p1)
    v[2] = 0  # игнорируем Z
    norm = np.linalg.norm(v)
    return v / norm if norm > 0 else v


# Угловой порог (в радианах)
angle_thresh = np.deg2rad(15)
target_dir = np.array([1, 0])  # направление вдоль X

lane_markings = [obj for obj in scene_objects if obj['type'] == 'lane_marking']

horizontal_markings = []
for obj in lane_markings:
    p1, p2 = obj['geometry']
    direction = get_direction(p1, p2)[:2]
    angle = np.arccos(np.clip(np.dot(direction, target_dir), -1.0, 1.0))
    if angle < angle_thresh:
        horizontal_markings.append(obj)

projected_segments_horizont = []

for obj in horizontal_markings:
    p1_3d, p2_3d = obj['geometry']
    p1_2d = camera.project_direct(PointND(p1_3d, add_weight=True)).get()
    p2_2d = camera.project_direct(PointND(p2_3d, add_weight=True)).get()

    if np.random.rand() < 0.5:  # 30% случаев — добавляем шум
        p1_2d += np.random.randint(-10, 10, size=2)
        p2_2d += np.random.randint(-10, 10, size=2)

    projected_segments_horizont.append([p1_2d, p2_2d])

projected_segments_pole = []
pole = [obj for obj in scene_objects if obj['type'] == 'pole']

for obj in pole:
    p1_3d, p2_3d = obj['geometry']
    p1_2d = camera.project_direct(PointND(p1_3d, add_weight=True)).get()
    p2_2d = camera.project_direct(PointND(p2_3d, add_weight=True)).get()

    if np.random.rand() < 0.5:  # 30% случаев — добавляем шум
        p1_2d += np.random.randint(-5, 10, size=2)
        p2_2d += np.random.randint(-5, 10, size=2)

    projected_segments_pole.append([p1_2d, p2_2d])

from source.vp_detection import VanishingPointEstimatorManual
from source.calibration import VanishingPointCalibration, RefineOptimizer, CalibrationPipeline
from source.calibration.refine import residual_interline_distance, residual_reprojection_line, \
    residual_reprojection_point, residual_line_length

vp1_manual = VanishingPointEstimatorManual().estimate(projected_segments_horizont[::5])
vp3_manual = VanishingPointEstimatorManual().estimate(projected_segments_pole[::5])
print(f'Точки схода: {vp1_manual, vp3_manual}')

camera_new = Camera(size=(1080, 1920))
vp_init = VanishingPointCalibration(camera_new)
vp_init.set_vanishing_points(vpX=vp1_manual, vpZ=vp3_manual)


def draw():
    global scale, p1, p2
    scale = 2
    ax.set_xlim(0, camera.size[1] * scale)
    ax.set_ylim(camera.size[0] * scale, -100)  # Важно: инвертируем ось Y, как в изображении
    ax.set_title("Проекция сцены на изображение (без фона)")
    ax.axis('off')
    ax.scatter(*vp1_manual, color='lime')
    ax.scatter(*vp3_manual, color='red')

    # Отрисовка
    for p1, p2 in projected_segments_horizont[::5]:
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='lime', linewidth=2)
    for p1, p2 in projected_segments_pole[::5]:
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='red', linewidth=2)
    plt.title("Горизонтальные линии разметки")
    plt.axis('off')
    plt.show()


# draw()  # Отрисовка

# ---------------
# 1 Точки схода + из точки в точку
# ---------------
pole = [obj for obj in scene_objects if obj['type'] == 'pole']

data_direct_optimize_point_to_point = []
for obj in pole:
    p1_3d, _ = obj['geometry']
    p1_2d = camera.project_direct(PointND(p1_3d, add_weight=True)).get()
    data_direct_optimize_point_to_point.append(
        {"pixel": p1_2d + np.random.randint(-10, 10, size=2), "gps": p1_3d + np.random.randint(-1, 1, size=3)})

data_direct_optimize = {
    "point_to_point": data_direct_optimize_point_to_point[:-5],
}

residualds_blocs = [
    lambda cam, data: np.array(residual_reprojection_point(cam, data, group='point_to_point'))

]

refine = RefineOptimizer(
    camera=camera_new,
    residual_blocks=residualds_blocs,
    mask=[0, 1, 2, 3, 6],
    bounds=[[500, -360, -360, -360, 10],
            [1500, 360, 360, 360, 27]],
    method='trf'
)

pipeline = CalibrationPipeline(
    init_stage=vp_init,
    refine_stages=[refine],
    n_iter=1,
)

# pipeline.run(camera_new, data_direct_optimize)

# ---------------
# 2 Точки схода + из точки в точку + расстояние м/у точками
# ---------------

pole = [obj for obj in scene_objects if obj['type'] == 'crosswalk']

crosswalk_dataset = []
for obj in pole:
    p1, p2, p3, p4 = obj['geometry']
    if np.linalg.norm(np.array(p1) - np.array(p4)) == 4:
        p1 = camera.project_direct(PointND(p1, add_weight=True)).get() + np.random.randint(-10, 10, size=2)
        p4 = camera.project_direct(PointND(p4, add_weight=True)).get() + np.random.randint(-10, 10, size=2)
        crosswalk_dataset.append([p1, p4])
    elif np.linalg.norm(np.array(p1) - np.array(p2)) == 4:
        p1 = camera.project_direct(PointND(p1, add_weight=True)).get() + np.random.randint(-10, 10, size=2)
        p2 = camera.project_direct(PointND(p2, add_weight=True)).get() + np.random.randint(-10, 10, size=2)
        crosswalk_dataset.append([p1, p2])

# ax.set_ylim(camera.size[0], -100)  # Важно: инвертируем ось Y, как в изображении
#
# for p1, p2 in crosswalk_dataset:
#     p1 = camera.project_direct(PointND(p1, add_weight=True)).get()
#     p2 = camera.project_direct(PointND(p2, add_weight=True)).get()
#     ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='lime', linewidth=2)
#
# plt.title("Горизонтальные линии разметки")
# plt.axis('off')
# plt.show()

data_direct_optimize = {
    "point_to_point": data_direct_optimize_point_to_point[::2],
    "line_length": crosswalk_dataset[::10],
}

residualds_blocs = [
    lambda cam, data: (
        np.array(residual_reprojection_point(cam, data, group='point_to_point')) * (1 / 100),
        'point_to_point'
    ),
    lambda cam, data: (np.array(residual_line_length(cam, data, group='line_length', expected=4)) * (1),
                       'line_length')
]

refine = RefineOptimizer(
    camera=camera_new,
    residual_blocks=residualds_blocs,
    mask=[0, 1, 2, 3, 6],
    bounds=[[500, -360, -360, -360, 10],
            [1500, 360, 360, 360, 27]],
    method='trf'
)

pipeline = CalibrationPipeline(
    init_stage=vp_init,
    refine_stages=[refine],
    n_iter=1,
)

# pipeline.run(camera=camera_new, data=data_direct_optimize)

from source.calibration.base import RESUALDS

# print(RESUALDS)

# # Объединяем в одну ось с цветом
# fig, ax = plt.subplots(figsize=(10, 5))
#
# last_step = max(RESUALDS)
#
# # Область 1 — point_to_point
# x1 = np.arange(len(RESUALDS[1]['point_to_point']))
# ax.plot(x1, RESUALDS[1]['point_to_point'], 'o-', label='point_to_point (step 1)')
# ax.plot(x1, RESUALDS[last_step]['point_to_point'], 's--', label='point_to_point (step last)')
#
# # Вертикальная линия раздела
# sep = len(x1)
#
# # Область 2 — line_length
# x2 = np.arange(len(RESUALDS[1]['line_length'])) + sep + 1
# ax.plot(x2, RESUALDS[1]['line_length'], 'o-', label='line_length (step 1)')
# ax.plot(x2, RESUALDS[last_step]['line_length'], 's--', label='line_length (step last)')
#
# # Оформление
# ax.axvline(sep + 0.5, color='gray', linestyle='--')
# ax.set_xticks(list(x1) + list(x2))
# ax.set_xticklabels([f'p{i}' for i in x1] + [f'l{i}' for i in range(len(x2))])
# ax.set_ylabel("Residual value")
# ax.set_title("Сравнение остатков на первом и последнем шаге")
# ax.legend()
# ax.grid(True)
#
# plt.tight_layout()
# plt.show()

# ---------------
# 3 Точки схода + из точки в точку + расстояние м/у линиями
# ---------------


for p1, p2 in full_lane_markings:
    p1 = camera.project_direct(PointND(p1, add_weight=True)).get()
    p2 = camera.project_direct(PointND(p2, add_weight=True)).get()
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='lime', linewidth=2)

plt.show()