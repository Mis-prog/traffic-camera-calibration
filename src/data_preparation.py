from .pointND import PointND

import numpy as np


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


def load_params(path):
    with open(path, 'r') as file:
        return [float(value) for value in file.readline().split()]


def prep_data_back_to_reverse(camera, data):
    data = np.array(data)
    data_calc = []
    for start, end in data:
        start_3d = camera.back_crop(start)
        end_3d = camera.back_crop(end)
        data_calc.append([camera.direct_crop(start_3d), camera.direct_crop(end_3d)])
    return np.array(data_calc)


def fun_lines(x, start: PointND, end: PointND):
    x1, y1 = start.get()
    x2, y2 = end.get()

    return (x - x1) * (y2 - y1) / (x2 - x1) + y1
