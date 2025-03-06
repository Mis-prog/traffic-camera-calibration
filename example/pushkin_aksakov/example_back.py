from src.camera_model import Camera
from src.optimizetion import Optimizer
from src.initsolution import calc_init_camera
from src.plot import Plot, DisplayMode
from src.pointND import PointND
from src.distance import gps_to_enu

import numpy as np


# camera = Camera()
# camera.load_scene('crossroads_not_dist.jpg')
# plot = Plot(camera)
# plot.visible(mode=DisplayMode.JUPYTER)

def load_data(path):
    lines = []
    with open(path, 'r') as file:
        for line in file:
            name, cords = line.split(':')
            points = eval(cords.strip())
            lines.append([PointND([x, y]) for x, y in points])
    return lines


def prep_data_angle(data):
    _data = []
    if len(data) % 2 == 0:
        for i in range(0, len(data), 2):
            _data.append(data[i] + data[i + 1])
        return np.array(_data)
    else:
        raise ValueError("Кол-во линий не четное число")


def prep_data_parallel(data):
    _data = []
    for i in range(0, len(data) - 1):
        _data.append(data[i] + data[i + 1])
    return np.array(_data)


data = {
    'angle': prep_data_angle(load_data('angle_lines.txt')),
    'parallel':prep_data_parallel(load_data('parallel_lines.txt'))
}