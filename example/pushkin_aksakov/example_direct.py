from src.camera_model import Camera
from src.optimizetion import Optimizer
from src.initsolution import calc_init_camera
from src.plot import Plot
from src.point3D import Point3D
from src.point2D import Point2D
from src.distance import gps_to_enu

import numpy as np

Line_Y = [[[297, 521], [1365, 272]], [[378, 555], [1462, 301]], [[417, 702], [1398, 430]], [[843, 894], [1343, 720]],
          [[1197, 283], [1396, 244]]]
Line_X = [[[755, 810], [601, 453]], [[1258, 962], [745, 315]], [[1388, 653], [1096, 345]], [[949, 268], [852, 179]]]

camera = calc_init_camera('../../data/crossroads_pushkin_aksakov/crossroads_not_dist.jpg', [Line_X, Line_Y])

# Опорная точка (центр локальной системы)
ref_lat, ref_lon = 54.723767, 55.933369

LINE_CALIB = [
    [[54.723767, 55.933369, 779, 874], [54.723936, 55.933454, 600, 452]],
    [[54.723767, 55.933369, 779, 874], [54.723714, 55.933668, 1399, 694]],
    [[54.723714, 55.933668, 1399, 694], [54.723884, 55.933750, 1084, 344]],
    [[54.723884, 55.933750, 1084, 344], [54.723936, 55.933454, 600, 452]],
    [[54.723854, 55.933420, 679, 625], [54.723804, 55.933712, 1222, 481]],
    [[54.723735, 55.933514, 1133, 790], [54.723917, 55.933596, 815, 394]],
    [[54.723863, 55.933352, 535, 668], [54.723793, 55.933774, 1320, 451]],
    [[54.723696, 55.933495, 1219, 911], [54.723957, 55.933613, 768, 340]],

    [[54.723889, 55.933191, 95, 803], [54.723761, 55.933949, 1565, 392]],

    [[54.723764, 55.933953, 1558, 386], [54.723847, 55.933996, 1395, 268]],

]

LINE_CALIB_NEW = []
# Переводим координаты первой линии в ENU
for line in LINE_CALIB:
    (lat1, lon1, x1, y1), (lat2, lon2, x2, y2) = line
    e1, n1 = gps_to_enu(lat1, lon1, ref_lat, ref_lon)
    e2, n2 = gps_to_enu(lat2, lon2, ref_lat, ref_lon)

    LINE_CALIB_NEW.append([[x1, y1, float(e1), float(n1), 0], [x2, y2, float(e2), float(n2), 0]])

LINE_PREP = []
for line in LINE_CALIB_NEW:
    start, end = line
    start2D, start3D = Point2D(start[0:2]), Point3D(start[2:6])
    end2D, end3D = Point2D(end[0:2]), Point3D(end[2:6])

    LINE_PREP.append([(start2D, start3D), (end2D, end3D)])

print(LINE_CALIB_NEW)
camera.set_params([905.78, -139.41, 18.27, -186.59, 4.81, 3.27, 27.09])
# optimize = Optimizer(camera)
# camera, info, cost_history, history = optimize.optimize_reprojection(LINE_PREP)
# print("Финальная ошибка:", info.cost)
# print("Финальные параметры:", np.around(info.x, 2))

plot = Plot(camera)
plot.draw_tranform_net(LINE_PREP, save=True)
# plot.draw_calibration_line(LINE_PREP, save=True)
#

# import matplotlib.pyplot as plt
#
# plt.plot(cost_history)
# plt.show()
