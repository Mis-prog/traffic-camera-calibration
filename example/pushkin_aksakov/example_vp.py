import numpy as np
import json
import os
import matplotlib.pyplot as plt
import cv2

from source.core import Camera
from source.calibration import VanishingPointEstimator, VanishingPointCalibration


def load_lines(filename):
    _filename = os.path.join("vp", filename)
    if not os.path.exists(_filename):
        print("Файл аннотаций не найден.")
        return

    with open(_filename, "r") as f:
        data = json.load(f)

    # Преобразуем строки ключей обратно в список линий
    lines = [[tuple(point) for point in line] for line in data.values()]
    return lines


def draw_coordinate_axes_from_vps(vanishing_points, center, scale=100, labels=None, colors=None, flip_z=True):
    """
    Рисует координатные оси X, Y, Z от центра изображения по направлению к точкам схода.

    :param vanishing_points: список [(x1, y1), (x2, y2), (x3, y3)] — координаты VP
    :param center: (cx, cy) — центр изображения (или центр проекции камеры)
    :param scale: длина стрелок (в пикселях)
    :param labels: подписи осей, по умолчанию ['X', 'Y', 'Z']
    :param colors: цвета осей, по умолчанию ['red', 'green', 'blue']
    """
    if labels is None:
        labels = ['X', 'Y', 'Z']
    if colors is None:
        colors = ['red', 'green', 'blue']

    cx, cy = center

    for i, (x, y) in enumerate(vanishing_points):
        dx = x - cx
        dy = y - cy
        norm = np.hypot(dx, dy)
        dx_scaled = dx / norm * scale
        dy_scaled = dy / norm * scale

        if flip_z and labels[i].upper() == 'Z':
            dx_scaled *= -1
            dy_scaled *= -1

        # Рисуем стрелку оси
        plt.arrow(cx, cy, dx_scaled, dy_scaled,
                  color=colors[i], width=1.2, head_width=10, length_includes_head=True)


lines_vp1 = load_lines("vp1.json")
lines_vp2 = load_lines("vp2.json")
lines_vp3 = load_lines("vp3.json")

vp1 = VanishingPointEstimator().estimate(lines_vp1)
vp2 = VanishingPointEstimator().estimate(lines_vp2)
vp3 = VanishingPointEstimator().estimate(lines_vp3)

plt.scatter(*vp1, label='vp manual', c='orange')
plt.scatter(*vp2, label='vp manual', c='orange')
plt.scatter(*vp3, label='vp manual', c='orange')

vp1 = [3974.185, -248.69977]
vp2 = [768.4042, 2362.912]
vp3 = [-24.940735, -669.0249]


plt.legend()
# plt.show()
camera = Camera('image/pattern_corrected_image.png')
calibrationVP = VanishingPointCalibration(camera)
calibrationVP.set_vanishing_points(vp1, vp2, vp3)
f = calibrationVP.calc_f()
camera.intrinsics.set_focal_length(f)
K = camera.intrinsics.get()
print(f'Фокусное расстояние:\n{f}')
R = np.array(calibrationVP.calc_R(f))
print(f'Матрица поворота:\n{R}')

VP1 = K @ R[:, 0]
VP1_pixel = [VP1[0] / VP1[2], VP1[1] / VP1[2]]

VP2 = K @ R[:, 1]
VP2_pixel = [VP2[0] / VP2[2], VP2[1] / VP2[2]]

V3_calc = np.dot(VP1, VP2)
VP3 = K @ R[:, 2]
VP3_pixel = [VP3[0] / VP3[2], VP3[1] / VP3[2]]

VP_opt = np.array([VP1_pixel, VP2_pixel, VP3_pixel])
plt.scatter(VP_opt[:, 0], VP_opt[:, 1])

image = camera.get_image()
image_height, image_width = camera.get_size()
center = (image_width // 2, image_height // 2)
draw_coordinate_axes_from_vps(VP_opt, center)
plt.imshow(image)
plt.show()
