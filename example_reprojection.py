from src.camera_model import Camera
from src.optimizetion import Optimizer
from src.initsolution import calc_init_camera
from src.plot import Plot
from src.point3D import Point3D
from src.point2D import Point2D

# Линии схода относительно направлений
Line_Y = [[[786, 689], [281, 515]], [[1061, 516], [213, 340]], [[1008, 421], [375, 311]], [[355, 264], [70, 238]],
          [[362, 223], [73, 211]]]
Line_X = [[[300, 513], [555, 185]], [[835, 677], [927, 264]], [[674, 117], [740, 13]], [[833, 192], [842, 158]],
          [[954, 142], [954, 38]]]

camera = calc_init_camera('data/crossroads_karls_marks/scene_from_crossroads_not_dist.png', [Line_X, Line_Y])


# Калибровочные линии
lines_calib = [
    [[831, 689, 7.71, 0, 0],
     [299, 520, 7.71, 20.7, 0]],
    [[896, 405, 18.9, 0, 0],
     [439, 322, 18.9, 20.7, 0]],
    [[927, 267, 31.9, 0, 0],
     [553, 189, 31.9, 20.7, 0]],
    [[890, 478, 15.09, 0, 0],
     [397, 379, 15.09, 20.7, 0]],
    [[300, 515, 7.71, 20.7, 0],
     [557, 180, 31.9, 20.7, 0]]
]

lines_prep = []
for line in lines_calib:
    start, end = line
    start2D, start3D = Point2D(start[0:2]), Point3D(start[2:6])
    end2D, end3D = Point2D(end[0:2]), Point3D(end[2:6])

    lines_prep.append([(start2D, start3D), (end2D, end3D)])

optimize = Optimizer(camera)
camera.set_params([931.45763154, -99.58434695, 37.91236625, -167.6947188, 31])

camera, info = optimize.optimize_reprojection(lines_prep)
print("Финальная ошибка:", info.cost)
print("Финальные параметры:", info.x)

plot = Plot(camera)
plot.draw_tranform_line(lines_prep)