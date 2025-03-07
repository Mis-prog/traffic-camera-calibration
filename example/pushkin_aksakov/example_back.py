from src.camera_model import Camera
from src.new_optimization import NewOptimization, RESIDUALS
from src.initsolution import calc_init_camera
from src.plot import Plot, DisplayMode, ProjectionMode
from src.pointND import PointND
from src.distance import gps_to_enu
from src.data_preparation import load_data, prep_data_parallel, prep_data_angle

import numpy as np
import matplotlib.pyplot as plt

data = {
    'angle': prep_data_angle(load_data('angle_lines.txt')),
    # 'parallel': prep_data_parallel(load_data('parallel_lines.txt')),
    'dist_between_line': prep_data_parallel(load_data('parallel_lines.txt'))
}

camera = Camera()
camera.load_scene('crossroads_not_dist.jpg')
plot = Plot(camera)
plot.draw_line(np.array(load_data('angle_lines.txt')))
plot.visible(DisplayMode.JUPYTER)
# optimize = NewOptimization(camera)
# optimize.back_projection(data)
#
# print(np.array(RESIDUALS))
# plt.plot(RESIDUALS[-1])
# plt.show()
