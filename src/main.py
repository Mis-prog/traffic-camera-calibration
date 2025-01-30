from camera import Camera
from optimizetion import Optimizer
from initsolution import calc_init_camera
from point import Point
from plot import Plot

# Линии схода относительно направлений
Line_Y = [[[786, 689], [281, 515]], [[1061, 516], [213, 340]], [[1008, 421], [375, 311]], [[355, 264], [70, 238]],
          [[362, 223], [73, 211]]]
Line_X = [[[300, 513], [555, 185]], [[835, 677], [927, 264]], [[674, 117], [740, 13]], [[833, 192], [842, 158]],
          [[954, 142], [954, 38]]]

camera = calc_init_camera('../data/scene_from_crossroads_not_dist.png', [Line_X, Line_Y])

# Получение углов
# camera.get_R(angle_output=True,output=True)

# Калибровочные линии
lines = [
    [[831, 689, 1, 7.71, 0, 0, 1],
     [299, 520, 1, 7.71, 20.7, 0, 1]],
    [[1007, 425, 1, 18.9, 0, 0, 1],
     [439, 322, 1, 18.9, 20.7, 0, 1]],
    [[927, 267, 1, 31.9, 0, 0, 1],
     [553, 189, 1, 31.9, 20.7, 0, 1]],
    [[890, 478, 1, 15.09, 0, 0, 1],
     [397, 379, 1, 15.09, 20.7, 0, 1]],
    [[300, 515, 1, 7.71, 20.7, 0, 1],
     [557, 183, 1, 31.9, 20.7, 0, 1]]
]

lines_from_Point = []
for line in lines:
    start_point, end_point = line
    start_point = Point.from_combined(start_point)
    end_point = Point.from_combined(end_point)
    lines_from_Point.append([start_point, end_point])

optimize = Optimizer(camera)

camera, info = optimize.optimize(lines_from_Point)

plot = Plot(camera)
plot.draw_tranform_coord(lines_from_Point,save=True)



