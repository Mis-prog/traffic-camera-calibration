from src.camera_model import Camera
from src.new_optimization import NewOptimization, RESIDUALS, PARAMS
from src.initsolution import calc_init_camera
from src.plot import Plot, DisplayMode, ProjectionMode
from src.pointND import PointND
from src.distance import gps_to_enu
from src.data_preparation import load_data, prep_data_parallel, prep_data_angle, load_params, prep_data_back_to_reverse

import numpy as np
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("TkAgg")

camera = Camera()
camera.load_scene('image/crossroads_not_dist_ver2.webp')

# Отрисовка исходных линий
plot = Plot(camera)
# plot.draw_line(load_data('marked_data/angle_lines.txt'))
plot.draw_line(load_data('marked_data/parallel_lines_1.txt'))
plot.draw_line(load_data('marked_data/parallel_lines_2.txt'))
plot.draw_line(load_data('marked_data/point_to_point.txt'))
plot.visible()

# Оптимизация
data = {
    # 'angle': prep_data_angle(load_data('marked_data/angle_lines.txt')),
    'parallel': prep_data_parallel(load_data('marked_data/parallel_lines_1.txt')),
    'point_to_point': np.array(load_data('marked_data/point_to_point.txt')),
    'parallel_2': prep_data_parallel(load_data('marked_data/parallel_lines_2.txt')),
}
optimize = NewOptimization(camera)
optimize.back_projection(data)

# # Отрисовка результатов оптимизации
HIST = [np.sum(values) for values in RESIDUALS]

plt.figure(1)
plt.subplot(1, 2, 1)
plt.plot(np.arange(0, len(HIST)), HIST)

plt.subplot(1, 2, 2)
plt.plot(RESIDUALS[0], label='Начальные остатки')
plt.plot(RESIDUALS[-1], label='Конечные остатки')
plt.legend()
plt.show()
PARAMS = np.array(PARAMS)

plt.plot(PARAMS[:, 0], label='Фокусное расстояние')
plt.plot(PARAMS[:, 1], label='Вращение вокруг Z')
plt.plot(PARAMS[:, 2], label='Вращение вокруг X')
plt.plot(PARAMS[:, 3], label='Вращение вокруг Y')
plt.plot(PARAMS[:, 4], label='Высота')
plt.legend()
plt.show()

# Тесты
# camera.set_params(load_params('marked_data/calib_data.txt'))
# optimize = NewOptimization(camera)
#
# data_calc = prep_data_back_to_reverse(camera,
#                                       load_data('marked_data/angle_lines.txt') + load_data(
#                                           'marked_data/parallel_lines.txt') + load_data(
#                                           'marked_data/point_to_point.txt'))
# plot = Plot(camera)
# plot.draw_line(data_calc, thickness=4)
# plot.draw_line(load_data('marked_data/angle_lines.txt'), color=(0, 255, 0))
# plot.draw_line(load_data('marked_data/parallel_lines.txt'), color=(0, 255, 0))
# plot.draw_line(load_data('marked_data/point_to_point.txt'), color=(0, 255, 0))
# plot.visible(DisplayMode.INTERACTIVE)

# data = load_data('calibration_lines.txt')
# print(np.linalg.norm(optimize._back_project_line_3d(*data[0], load_params('calib_data.txt'))))

# Прямая линия

# camera = Camera()
# camera.load_scene('image/crossroads_ver2.jpg')
camera.set_params(load_params('marked_data/calib_data.txt'))

plot_coord = []
for start, end in load_data('marked_data/parallel_lines_1.txt'):
    start3d = camera.back_crop(start)
    end3d = camera.back_crop(end)
    plot_coord.append([start3d, end3d])

for i in range(1, len(plot_coord)):
    start1, end1 = plot_coord[i - 1]
    start2, end2 = plot_coord[i]
    plt.plot([start1.get()[0], end1.get()[0]], [start1.get()[1], end1.get()[1]],
             label=f'Расстояние\nНачало: {np.linalg.norm(start2.get() - start1.get())}\nКонец:  {np.linalg.norm(end2.get() - end1.get())}')
    plt.scatter(start1.get()[0], start1.get()[1])
start2, end2 = plot_coord[-1]
plt.plot([start2.get()[0], end2.get()[0]], [start2.get()[1], end2.get()[1]])

plt.legend()
plt.show()
