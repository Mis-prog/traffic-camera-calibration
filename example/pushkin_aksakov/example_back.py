from src.camera_model import Camera
from src.new_optimization import NewOptimization, RESIDUALS, PARAMS
from src.initsolution import calc_init_camera
from src.plot import Plot, DisplayMode, ProjectionMode
from src.pointND import PointND
from src.distance import gps_to_enu
from src.data_preparation import load_data, prep_data_parallel, prep_data_angle

import numpy as np
import matplotlib.pyplot as plt

data = {
    'angle': prep_data_angle(load_data('angle_lines.txt')),
    'parallel': prep_data_parallel(load_data('parallel_lines.txt')),
    'point_to_point': np.array(load_data('point_to_point.txt'))
}

camera = Camera()
camera.load_scene('crossroads_not_dist.jpg')
plot = Plot(camera)
plot.draw_line(load_data('angle_lines.txt'))
plot.draw_line(load_data('parallel_lines.txt'))
plot.draw_line(load_data('point_to_point.txt'))

plot.visible()
optimize = NewOptimization(camera)
optimize.back_projection(data)

HIST = [np.sum(values) for values in RESIDUALS]

plt.figure(1)
plt.subplot(1, 2, 1)
plt.plot(np.arange(0, len(HIST)), HIST)

plt.subplot(1, 2, 2)
plt.plot(RESIDUALS[0], label='Начальные остатки')
plt.plot(RESIDUALS[-1], label='Конечные остатки')
plt.legend()
plt.show()

# PARAMS = np.array(PARAMS)
#
# plt.plot(PARAMS[:, 0], label='Фокусное расстояние')
# plt.plot(PARAMS[:, 1], label='Вращение вокруг Z')
# plt.plot(PARAMS[:, 2], label='Вращение вокруг X')
# plt.plot(PARAMS[:, 3], label='Вращение вокруг Y')
# plt.plot(PARAMS[:, 4], label='Высота')
# plt.legend()
# plt.show()
