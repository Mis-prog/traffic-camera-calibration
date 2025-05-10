from source.camera_model import Camera
from source.calibration.direct_optimizatoin import DirectProjectionOptimizer
from source.utils.initsolution import calc_init_camera
from source.plot import Plot
from source.pointND import PointND
from source.utils.distance import gps_to_enu

import numpy as np

# Line_Y = [[[297, 521], [1365, 272]], [[378, 555], [1462, 301]], [[417, 702], [1398, 430]], [[843, 894], [1343, 720]],
#           [[1197, 283], [1396, 244]]]
# Line_X = [[[755, 810], [601, 453]], [[1258, 962], [745, 315]], [[1388, 653], [1096, 345]], [[949, 268], [852, 179]]]
#
# camera = calc_init_camera('../../data/crossroads_pushkin_aksakov/crossroads_not_dist.jpg', [Line_X, Line_Y])
#
# # Опорная точка (центр локальной системы)
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
    # [[54.723889, 55.933191, 95, 803], [54.723761, 55.933949, 1565, 392]],
    # [[54.723764, 55.933953, 1558, 386], [54.723847, 55.933996, 1395, 268]],
]
#
LINE_CALIB_NEW = []
# Переводим координаты первой линии в ENU
for line in LINE_CALIB:
    (lat1, lon1, x1, y1), (lat2, lon2, x2, y2) = line
    e1, n1 = gps_to_enu(lat1, lon1, ref_lat, ref_lon)
    e2, n2 = gps_to_enu(lat2, lon2, ref_lat, ref_lon)

    LINE_CALIB_NEW.append([[x1, y1, float(e1), float(n1), 0], [x2, y2, float(e2), float(n2), 0]])
#
LINE_PREP = []
for line in LINE_CALIB_NEW:
    start, end = line
    start2D, start3D = PointND(start[0:2]), PointND(start[2:6])
    end2D, end3D = PointND(end[0:2]), PointND(end[2:6])

    LINE_PREP.append([(start2D, start3D), (end2D, end3D)])
#
# print(LINE_CALIB_NEW)
camera = Camera('image/pattern_corrected_image.png')
camera.set_params([929.67, -141.65, 17.12, -186.47, 5.31, 3.68, 27.73])
optimize = DirectProjectionOptimizer(camera)
camera, info, cost_history, history = optimize.optimize_reprojection(LINE_PREP)
print("Финальная ошибка:", info.cost)
print("Финальные параметры:", np.around(info.x, 2))
#
# plot = Plot(camera)
# plot.draw_tranform_line(LINE_PREP, save=True)
# plot.draw_calibration_line(LINE_PREP, save=True)
#
# #
# import matplotlib.pyplot as plt
#
# plt.plot(np.arange(0, len(cost_history)), np.log(cost_history))
# plt.ylabel('Точность')
# plt.xlabel('Количество итераций')
# plt.show()

import matplotlib.pyplot as plt
import cv2

image = cv2.imread('image/pattern_corrected_image.png')
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

image_width = 1920
image_height = 1080

camera = Camera('image/pattern_corrected_image.png')
camera.set_params([1419.59, -142.56, 49.5, -185.62, -12.82, -18.38, 30.63])


K = camera.get_A()
print(f'Matrix intrinsics:\n{K}')
R = camera.get_R()
print(f'Matrix rot:\n{R}')

C = np.array([[-12.82], [-18.38], [30.63]])  # столбец, чтобы собрать [R | t]
t = -R @ C  # вектор переноса (перевод центра камеры в систему камеры)
Rt = np.hstack((R, t))  # 3x4 матрица [R | t]
P = K @ Rt
VP1 = K @ R[:, 0]
VP1_pixel = [VP1[0] / VP1[2], VP1[1] / VP1[2]]

VP2 = K @ R[:, 1]
VP2_pixel = [VP2[0] / VP2[2], VP2[1] / VP2[2]]

V3_calc = np.dot(VP1, VP2)
VP3 = K @ R[:, 2]
VP3_pixel = [VP3[0] / VP3[2], VP3[1] / VP3[2]]

plt.xlim(0, image_width)
plt.ylim(image_height, 0)
plt.imshow(image_rgb)

plt.scatter(VP1_pixel[0], VP1_pixel[1], c='red', label='VP1')
plt.scatter(VP2_pixel[0], VP2_pixel[1], c='green', label='VP2')
plt.scatter(VP3_pixel[0], VP3_pixel[1], c='blue', label='VP3')

# Отметим центральную точку
plt.scatter(image_width // 2, image_height // 2, c='black', marker='o', label='Центр')



# Показать изображение

origin = np.array([0, 0, 0, 1])  # гомогенные координаты
length = 10 # длина векторов в 3D (в условных единицах)

# 3D-концы векторов осей
x_axis_end = np.array([length, 0, 0])
y_axis_end = np.array([0, length, 0])
z_axis_end = np.array([0, 0, length])


def project_point(p3d):
    p = P @ np.append(p3d, 1)
    return p[:2] / p[2]

# Центр камеры в изображении
center_pixel = project_point([0, 0, 0])
x_pixel = project_point(x_axis_end)
y_pixel = project_point(y_axis_end)
z_pixel = project_point(z_axis_end)

# Рисуем оси
plt.arrow(center_pixel[0], center_pixel[1], x_pixel[0] - center_pixel[0], x_pixel[1] - center_pixel[1],
          color='red', width=5, label='X')
plt.arrow(center_pixel[0], center_pixel[1], y_pixel[0] - center_pixel[0], y_pixel[1] - center_pixel[1],
          color='green', width=5, label='Y')
plt.arrow(center_pixel[0], center_pixel[1], z_pixel[0] - center_pixel[0], z_pixel[1] - center_pixel[1],
          color='blue', width=5, label='Z')

plt.legend()

plt.show()

def pixel_to_world(px, K, R, C, plane_normal=np.array([0, 0, 1]), plane_point=np.array([0, 0, 0])):
    """
    Проецирует пиксель px = [u,v] на плоскость, задаваемую normal и точкой на плоскости.
    """
    u, v = px
    K_inv = np.linalg.inv(K)

    # Луч в координатах камеры
    d_c = K_inv @ np.array([u, v, 1])

    # Перевод в мировую систему
    d_w = R.T @ d_c
    d_w = d_w / np.linalg.norm(d_w)  # желательно нормализовать

    # Центр камеры
    C = C.reshape((3, ))

    # Решаем пересечение прямой с плоскостью
    numerator = np.dot(plane_normal, (plane_point - C))
    denominator = np.dot(plane_normal, d_w)
    lam = numerator / denominator

    point_world = C + lam * d_w
    return point_world


px = [1000, 500]  # пиксель
C_world = np.array([-12.82, -18.38, 30.63])
pt_world = pixel_to_world(px, K, R, C_world)

print("3D координаты:", pt_world)