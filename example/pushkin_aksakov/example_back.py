from core.camera_model import Camera
from source.utils.data_preparation import load_data, prep_data_parallel
from calibration.refine.back.back_optimization import BackProjectionOptimizer

import numpy as np

# matplotlib.use("TkAgg")

camera = Camera('image/pattern_corrected_image.png')

# Отрисовка исходных линий
# plot = Plot(camera)
# plot.draw_line(load_data('marked_data_4/parallel_lines_1.txt'))
# plot.draw_line(load_data('marked_data_4/parallel_lines_2.txt'))
# plot.draw_line(load_data('marked_data_4/parallel_lines_3.txt'))
# # plot.draw_line(load_data('marked_data_4/parallel_lines_4.txt'))
# plot.draw_line(load_data('marked_data_4/point_to_point.txt'))
# plot.visible()

data = {
    # 'angle': prep_data_angle(load_data(('marked_data_3/angle_lines.txt'))),
    'parallel-1': prep_data_parallel(load_data('marked_data_4/parallel_lines_1.txt')),
    'point_to_point': np.array(load_data('marked_data_4/point_to_point.txt')),
    'parallel-2': prep_data_parallel(load_data('marked_data_4/parallel_lines_2.txt')),
    'parallel-3': prep_data_parallel(load_data('marked_data_4/parallel_lines_3.txt')),
    # 'parallel-4': prep_data_parallel(load_data('marked_data_4/parallel_lines_4.txt')),
    # 'parallel-4': prep_data_parallel(load_data('marked_data/parallel_lines_1.txt')),
    # 'parallel-5': prep_data_parallel(load_data('marked_data/parallel_lines_2.txt')),
    # 'point_to_point_2': np.array(load_data('marked_data/point_to_point.txt'))
}
# # Оптимизация
#

camera.calc_R([-158.07642684,   49.78161572,  173.91438536])
optimize = BackProjectionOptimizer(camera)
optimize.back_projection(data)
# #
# # # # Отрисовка результатов оптимизации
# HIST = [np.sum(values) for values in RESIDUALS]
#
# plt.figure(1)
# plt.subplot(1, 2, 1)
# plt.title('График погрешности')
# plt.ylabel('Точность')
# plt.xlabel('Количество итераций')
# plt.plot(np.arange(0, len(HIST)), HIST)
#
# plt.subplot(1, 2, 2)
# plt.plot(RESIDUALS[0], label='Первая итерация')
# plt.plot(RESIDUALS[-1], label='Последняя итерация')
# plt.axvspan(0, 3, color='lightgrey', alpha=0.5,label='Параллельные прямые')
# # plt.axvspan(1, 3, color='lightgrey', alpha=0.5)
# plt.axvspan(3, 14, color='darkgrey', alpha=0.5,label='Расстояние от точки до точки')
# # plt.axvline(x=1, color='black', linestyle='--')  # Вертикальная линия на X=5
# # plt.axvline(x=3, color='black', linestyle='--')
# plt.text(2.5, 12, 'Область 1', horizontalalignment='center', verticalalignment='center', color='black', fontsize=10)
# plt.text(7.5, 12, 'Область 2', horizontalalignment='center', verticalalignment='center', color='black', fontsize=10)
# plt.title('Погрешность для всех наборов данных')
# plt.ylabel('Погрешность')
# plt.xlabel('Наборы данных')
# plt.legend()
# plt.show()
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
