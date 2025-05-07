from source.camera_model import Camera
from source.data_preparation import load_data, prep_data_parallel, load_params, fun_lines
from source.plot import Plot
from source.pointND import PointND
from source.calibration.back_optimization import BackProjectionOptimizer, RESIDUALS, PARAMS

import numpy as np
import matplotlib
import cv2
import matplotlib.pyplot as plt

camera = Camera()
camera.load_scene('image/crossroads.jpg')
camera.set_params(load_params('marked_data/calib_data.txt'))
#
# scene = cv2.imread('image/image.webp')
# scene_rgb = cv2.cvtColor(scene, cv2.COLOR_BGR2RGB)
# plt.imshow(scene_rgb)


def line_params(start, end):
    # Прямые линии проходят через два заданных пункта (start, end)
    x1, y1 = start.get()
    x2, y2 = end.get()
    m = (y2 - y1) / (x2 - x1)  # угловой коэффициент
    b = y1 - m * x1  # пересечение с осью Y
    return m, b


# Функция для нахождения пересечения двух прямых
def intersection(m1, b1, m2, b2):
    # Решение системы уравнений m1*x + b1 = m2*x + b2
    x_intersection = (b2 - b1) / (m1 - m2)
    y_intersection = m1 * x_intersection + b1
    return x_intersection, y_intersection


# Загружаем данные
start1, end1 = load_data('marked_data/parallel_lines_2.txt')[1]
start2, end2 = load_data('marked_data/parallel_lines_1.txt')[1]

# Вычисляем параметры для обеих линий
m1, b1 = line_params(start1, end1)
m2, b2 = line_params(start2, end2)

# Находим точку пересечения
x_int, y_int = intersection(m1, b1, m2, b2)

for y_dist in [-7, 0, 7]:
    start, end = load_data('marked_data/parallel_lines_2.txt')[1]
    start3d = camera.back_crop(start)
    end3d = camera.back_crop(end)
    x = np.linspace(-50, 50, 100)
    y = fun_lines(x, start3d, end3d) - y_dist
    # plt.plot(x, y)
    points = [camera.direct_crop(PointND([xi, yi])) for xi, yi in zip(x, y)]
    x_new, y_new = zip(*[p.get() for p in points])
    if y_dist == 0:
        plt.plot(x_new, y_new, color='red')
    else:
        plt.plot(x_new, y_new, color='black')

for y_dist in [-11, 0, 11]:
    start, end = load_data('marked_data/parallel_lines_1.txt')[1]
    start3d = camera.back_crop(start)
    end3d = camera.back_crop(end)
    x = np.linspace(-50, 50, 100)
    y = fun_lines(x, start3d, end3d) - y_dist
    # plt.plot(x, y)
    points = [camera.direct_crop(PointND([xi, yi])) for xi, yi in zip(x, y)]
    x_new, y_new = zip(*[p.get() for p in points])
    if y_dist == 0:
        plt.plot(x_new, y_new, color='red')
    else:
        plt.plot(x_new, y_new, color='black')

# plt.plot(x_int, y_int, 'ro')
#
# plt.xlim(0, 1920)
# plt.ylim(0, 1080)
# plt.gca().invert_yaxis()
plt.show()
