from source.optimizetion import Optimizer
from source.utils.initsolution import calc_init_camera
from visualization.plot import CameraPlotter
from source.point3D import Point3D
from source.point2D import Point2D

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
    [[896, 405, 19.5, 0, 0],
     [439, 322, 19.5, 20.7, 0]],
    [[927, 267, 33, 0, 0],
     [553, 189, 33, 20.7, 0]],
    [[890, 478, 16, 0, 0],
     [397, 379, 16, 20.7, 0]],
    [[300, 515, 7.71, 20.7, 0],
     [557, 180, 31.9, 20.7, 0]]
]

# Калибровочные линии z = 0
lines_calib_z0 = [
    [[831, 689, 7.71, 0],
     [299, 520, 7.71, 20.7]],
    [[896, 405, 19.5, 0],
     [439, 322, 19.5, 20.7]],
    [[927, 267, 33, 0],
     [553, 189, 33, 20.7]],
    [[890, 478, 16, 0],
     [397, 379, 16, 20.7]],
    [[300, 515, 7.71, 20.7],
     [557, 180, 31.9, 20.7]]
]

# lines_calib_z0 = [
#     [[856, 606, 0, 0],
#      [980, 636, 3.9, 0]],
#     [[925, 290, 0, 0],
#      [1011, 306, 3.9, 0]],
#     [[824, 191, 0, 0],
#      [834, 155, 3.9, 0]],
#     [[257, 462, 0, 0],
#      [320, 485, 3.9, 0]],
#     [[375, 315, 0, 0],
#      [437, 326, 3.9, 0]],
#     [[490, 192, 0, 0],
#      [546, 196, 3.9, 0]],
#     [[844, 649, 0, 0],
#      [974, 678, 3.9, 0]],
#     [[301, 514, 0, 0],
#      [557, 183, 0, 25]],
# ]

lines_prep = []
for line in lines_calib:
    start, end = line
    start2D, start3D = Point2D(start[0:2]), Point3D(start[2:6])
    end2D, end3D = Point2D(end[0:2]), Point3D(end[2:6])

    lines_prep.append([(start2D, start3D), (end2D, end3D)])

lines_prep_z0 = []
for line in lines_calib_z0:
    start, end = line
    start2D, start3D = Point2D(start[0:2]), Point2D(start[2:5])
    end2D, end3D = Point2D(end[0:2]), Point2D(end[2:5])

    lines_prep_z0.append([(start2D, start3D), (end2D, end3D)])

# camera.set_params([1245.17236388, -107.24442581, 31.13531922, -171.60155562, 38.20672058])
camera.set_params([931.45763154, -99.58434695, 37.91236625, -167.6947188, 31])
optimize = Optimizer(camera)
camera, info = optimize.optimize_back_reprojection_NM(lines_prep_z0)

print("Финальные параметры:", info.x)

# lines_calib = [
#     [[831, 689, 7.71, 0, 0],
#      [299, 520, 7.71, 20.7, 0]],
#     [[896, 405, 18.9, 0, 0],
#      [439, 322, 18.9, 20.7, 0]],
#     [[927, 267, 31.9, 0, 0],
#      [553, 189, 31.9, 20.7, 0]],
#     [[890, 478, 15.09, 0, 0],
#      [397, 379, 15.09, 20.7, 0]],
#     [[300, 515, 7.71, 20.7, 0],
#      [557, 180, 31.9, 20.7, 0]]
# ]
#
# lines_prep = []
# for line in lines_calib:
#     start, end = line
#     start2D, start3D = Point2D(start[0:2]), Point3D(start[2:6])
#     end2D, end3D = Point2D(end[0:2]), Point3D(end[2:6])
#
#     lines_prep.append([(start2D, start3D), (end2D, end3D)])
plot = CameraPlotter(camera)
plot.draw_tranform_line(lines_prep)
