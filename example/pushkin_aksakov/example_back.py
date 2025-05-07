from source.camera_model import Camera
from source.data_preparation import load_data, prep_data_parallel, load_params, fun_lines, prep_data_angle
from source.plot import Plot
from source.pointND import PointND
from source.calibration.back_optimization import BackProjectionOptimizer, RESIDUALS, PARAMS

import numpy as np
import matplotlib
import cv2
import matplotlib.pyplot as plt

matplotlib.use("TkAgg")

camera = Camera()
camera.load_scene('image/building_corrected_image.png')

# Отрисовка исходных линий
plot = Plot(camera)
plot.draw_line(load_data('marked_data_3/parallel_lines_1.txt'))
plot.draw_line(load_data('marked_data_3/parallel_lines_2.txt'))
# plot.draw_line(load_data('marked_data_3/parallel_lines_3.txt'))
plot.draw_line(load_data('marked_data_3/parallel_lines_4.txt'))
plot.draw_line(load_data('marked_data_3/point_to_point.txt'))
plot.visible()

data = {
    # 'angle': prep_data_angle(load_data(('marked_data_3/angle_lines.txt'))),
    'parallel-1': prep_data_parallel(load_data('marked_data_3/parallel_lines_1.txt')),
    'point_to_point': np.array(load_data('marked_data_3/point_to_point.txt')),
    'parallel-2': prep_data_parallel(load_data('marked_data_3/parallel_lines_2.txt')),
    'parallel-3': prep_data_parallel(load_data('marked_data_3/parallel_lines_3.txt')),
    'parallel-4': prep_data_parallel(load_data('marked_data_3/parallel_lines_4.txt')),
    # 'parallel-4': prep_data_parallel(load_data('marked_data/parallel_lines_1.txt')),
    # 'parallel-5': prep_data_parallel(load_data('marked_data/parallel_lines_2.txt')),
    # 'point_to_point_2': np.array(load_data('marked_data/point_to_point.txt'))
}
# Оптимизация

optimize = BackProjectionOptimizer(camera)
optimize.back_projection(data)
# #
# # # # Отрисовка результатов оптимизации
HIST = [np.sum(values) for values in RESIDUALS]

plt.figure(1)
plt.subplot(1, 2, 1)
plt.title('График погрешности')
plt.ylabel('Точность')
plt.xlabel('Количество итераций')
plt.plot(np.arange(0, len(HIST)), HIST)

plt.subplot(1, 2, 2)
plt.plot(RESIDUALS[0], label='Первая итерация')
plt.plot(RESIDUALS[-1], label='Последняя итерация')
plt.axvspan(0, 3, color='lightgrey', alpha=0.5,label='Параллельные прямые')
# plt.axvspan(1, 3, color='lightgrey', alpha=0.5)
plt.axvspan(3, 14, color='darkgrey', alpha=0.5,label='Расстояние от точки до точки')
# plt.axvline(x=1, color='black', linestyle='--')  # Вертикальная линия на X=5
# plt.axvline(x=3, color='black', linestyle='--')
plt.text(2.5, 12, 'Область 1', horizontalalignment='center', verticalalignment='center', color='black', fontsize=10)
plt.text(7.5, 12, 'Область 2', horizontalalignment='center', verticalalignment='center', color='black', fontsize=10)
plt.title('Погрешность для всех наборов данных')
plt.ylabel('Погрешность')
plt.xlabel('Наборы данных')
plt.legend()
plt.show()
# PARAMS = np.array(PARAMS)
# #
# plt.plot(PARAMS[:, 0], label='f')
# plt.plot(PARAMS[:, 1], label='Z')
# plt.plot(PARAMS[:, 2], label='X')
# plt.plot(PARAMS[:, 3], label='Y')
# plt.plot(PARAMS[:, 4], label='H')
# plt.legend()
# plt.show()

# Тесты
# camera.set_params(load_params('marked_data/calib_data.txt'))
# optimize = NewOptimization(camera)
#
# data_calc = prep_data_back_to_reverse(camera,
#                                       load_data('marked_data/point_to_point.txt') + load_data(
#                                           'marked_data/parallel_lines_1.txt') + load_data(
#                                           'marked_data/parallel_lines_2.txt'))
# plot = Plot(camera)
# plot.draw_line(data_calc, thickness=7)
# plot.draw_line(load_data('marked_data/parallel_lines_1.txt'), color=(0, 255, 0))
# plot.draw_line(load_data('marked_data/parallel_lines_2.txt'), color=(0, 255, 0))
# plot.draw_line(load_data('marked_data/point_to_point.txt'), color=(0, 255, 0))
# plot.visible(DisplayMode.INTERACTIVE)

# data = load_data('calibration_lines.txt')
# print(np.linalg.norm(optimize._back_project_line_3d(*data[0], load_params('calib_data.txt'))))

# Прямая линия
# camera = Camera()
# camera.load_scene('image/image.webp')
# print(load_params('marked_data/calib_data.txt'))
# camera.set_params(load_params('marked_data/calib_data.txt'))
#
# plot_coord = []
# for start, end in load_data('marked_data/parallel_lines_1.txt'):
#     start3d = camera.back_crop(start)
#     end3d = camera.back_crop(end)
#     plot_coord.append([start3d, end3d])
#
# for i in range(1, len(plot_coord)):
#     start1, end1 = plot_coord[i - 1]
#     start2, end2 = plot_coord[i]
#     plt.plot([start1.get()[0], end1.get()[0]], [start1.get()[1], end1.get()[1]],
#              label=f'Расстояние\nНачало: {np.linalg.norm(start2.get() - start1.get())}\nКонец:  {np.linalg.norm(end2.get() - end1.get())}')
#     plt.scatter(start1.get()[0], start1.get()[1])
# start2, end2 = plot_coord[-1]
# plt.plot([start2.get()[0], end2.get()[0]], [start2.get()[1], end2.get()[1]])


# Прямая линия продолжение

camera = Camera()
camera.load_scene('image/building_corrected_image.png')
camera.set_params(load_params('marked_data_new/calib_data.txt'))

scene = cv2.imread('image/building_corrected_image.png')
scene_rgb = cv2.cvtColor(scene, cv2.COLOR_BGR2RGB)
plt.imshow(scene_rgb)

# for i, (start, end) in enumerate(load_data('marked_data/parallel_lines_2.txt')):
#     start3d = camera.back_crop(start)
#     end3d = camera.back_crop(end)
#     x = np.linspace(-100, 100, 100)
#     y = fun_lines(x, start3d, end3d)
#     points = [camera.direct_crop(PointND([xi, yi])) for xi, yi in zip(x, y)]
#     x_new, y_new = zip(*[p.get() for p in points])
#     plt.scatter([start.get()[0], end.get()[0]], [start.get()[1], end.get()[1]])
#     plt.plot(x_new, y_new, label=f'Transformed Line 1 - {i}')
# coord1.append(np.array([x, y]))

# На известных данных
for y_dist in [-80, 0, 80]:
    start, end = load_data('marked_data/parallel_lines_2.txt')[1]
    start3d = camera.back_crop(start)
    end3d = camera.back_crop(end)
    x = np.linspace(-1000, 1000, 100)
    y = fun_lines(x, start3d, end3d) - y_dist

    plt.plot(x, y)
    plt.scatter(*start3d.get())
    plt.scatter(*end3d.get())
    plt.scatter(*start.get())
    plt.scatter(*end.get())

    points = [camera.direct_crop(PointND([xi, yi])) for xi, yi in zip(x, y)]
    x_new, y_new = zip(*[p.get() for p in points])
    if y_dist == 0:
        plt.plot(x_new, y_new, color='red')
    else:
        plt.plot(x_new, y_new, color='black')

for y_dist in [-100, 0, 100]:
    start, end = load_data('marked_data/parallel_lines_1.txt')[1]
    start3d = camera.back_crop(start)
    end3d = camera.back_crop(end)
    x = np.linspace(-1000, 1000, 100)
    y = fun_lines(x, start3d, end3d) - y_dist

    plt.plot(x, y)
    plt.scatter(*start3d.get())
    plt.scatter(*end3d.get())
    plt.scatter(*start.get())
    plt.scatter(*end.get())

    points = [camera.direct_crop(PointND([xi, yi])) for xi, yi in zip(x, y)]
    x_new, y_new = zip(*[p.get() for p in points])
    if y_dist == 0:
        plt.plot(x_new, y_new, color='red')
    else:
        plt.plot(x_new, y_new, color='black')

plt.xlim(0, 1920)
plt.ylim(0, 1080)
plt.gca().invert_yaxis()
plt.show()

# # Создание синтетических данных
# camera = Camera()
# camera.load_scene('image/image.webp')
# camera.set_params(load_params('marked_data/calib_data.txt'))
#
# start, end = load_data('marked_data/parallel_lines_1.txt')[1]
# start3d = camera.back_crop(start)
# end3d = camera.back_crop(end)
#
# print(np.linalg.norm(end3d.get() - start3d.get()))
# y_dist = 0
# x = np.linspace(-25, 25, 100)
# y = fun_lines(x, start3d, end3d) - y_dist
# points = [camera.direct_crop(PointND([xi, yi])) for xi, yi in zip(x, y)]
# x_new, y_new = zip(*[p.get() for p in points])
# plt.plot([start3d.get()[0], end3d.get()[0]], [start3d.get()[1], end3d.get()[1]])
# plt.plot(x, y)
# plt.show()
