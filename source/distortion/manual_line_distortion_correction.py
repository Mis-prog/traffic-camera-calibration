import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize


def linear_interpolation(x, line):
    (x1, y1), (x2, y2) = line
    if x1 <= x <= x2 or x2 <= x <= x1:
        m = (y2 - y1) / (x2 - x1)
        b = y1 - m * x1
        y = m * x + b
        return y
    else:
        raise ValueError("x is out of bounds of the line segment")


def undistort_image(image, K, dist_coeffs):
    return cv2.undistort(image, K, dist_coeffs)


def set_params(params):
    """
    fx, fy, cx, cy, k1, k2, p1, p2, k3 = params
    """
    if len(params) == 9:
        optimized_K = np.array([[params[0], 0, params[2]],
                                [0, params[1], params[3]],
                                [0, 0, 1]], dtype=np.float32)
        optimized_dist_coeffs = np.array([params[4], params[5], params[6], params[7], params[8]], dtype=np.float32)
        return optimized_K, optimized_dist_coeffs
    else:
        raise ValueError("Длина вектора параметров не равняется 9")


def undistort_point(point, K, dist_coeffs):
    point = np.array(point, dtype=np.float32).reshape(-1, 1, 2)  # Передаем точку как массив
    undistorted_point = cv2.undistortPoints(point, K, dist_coeffs)

    # Преобразуем нормализованные координаты в пиксельные
    undistorted_point_pixels = cv2.convertPointsToHomogeneous(undistorted_point)
    undistorted_point_pixels = np.dot(undistorted_point_pixels, K.T)

    pixel_coords = undistorted_point_pixels[0, 0]
    return pixel_coords[:2]  # Возвращаем только пиксельные координаты


def distortion_error(params, x_vals, y_vals, line):
    optimized_K, optimized_dist_coeffs = set_params(params)

    undistorted_points = []
    for x, y in zip(x_vals, y_vals):
        undistorted_point = undistort_point([x, y], optimized_K, optimized_dist_coeffs)
        undistorted_points.append(undistorted_point)

    error = []
    for undistorted_point, x in zip(undistorted_points, x_vals):
        predicted_y = linear_interpolation(x, line)  # Линейная интерполяция для синих точек
        error.append((undistorted_point[1] - predicted_y) ** 2)  # Ошибка по оси Y

    return np.sum(error) / len(error)


def target_error(params, data):
    error = 0
    for x_vals, y_vals, line in data:
        error = distortion_error(params, x_vals, y_vals, line) + error
    return error


# Данные для синих и красных линий
line1 = [(2, 822), (1916, 302)]  # Синие линии
line2 = [(1077, 344), (1390, 671)]  # Красные линии

image = cv2.imread('screenshot_1747025981351.png')
size = list(image.shape[:2])
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# # Интерполяция для синих и красных линий
# x_line1 = np.linspace(line1[0][0], line1[1][0], 100)
# y_line1 = [linear_interpolation(x, line1) for x in x_line1]
# x_line2 = np.linspace(line2[0][0], line2[1][0], 100)
# y_line2 = [linear_interpolation(x, line2) for x in x_line2]
#
# # Подготовка к оптимизации
# points = np.loadtxt('points_line1.csv', delimiter=',')
# x = points[:, 0]
# y = points[:, 1]
#
# degree = 4
# coefficients = np.polyfit(x, y, degree)
# poly = np.poly1d(coefficients)
# y_fit_line1 = poly(x_line1)
#
# points = np.loadtxt('points_line2.csv', delimiter=',')
# x = points[:, 0]
# y = points[:, 1]
#
# coefficients = np.polyfit(x, y, degree)
# poly = np.poly1d(coefficients)
# y_fit_line2 = poly(x_line2)
#
# # Минимизация ошибки с помощью least_squares
# initial_params = [1419, 1419, size[1] / 2, size[0] / 2, -0.1, 0.1, 0, 0, 0]  # Начальные коэффициенты для оптимизации
# print(f'Начальные параметры:\n{initial_params}')
# data = [
#     (x_line1, y_fit_line1, line1),
#     (x_line2, y_fit_line2, line2)
# ]
# result = minimize(target_error, initial_params, args=(data), method='Nelder-Mead')
# print(result)
# print(f'Конечные параметры:\n{result.x}')

optimized_K, optimized_dist_coeffs = set_params([1400, 1400, size[1] / 2, size[0] / 2, -0.43, 0, 0, 0, 0])
image_optim = undistort_image(image_rgb, optimized_K, optimized_dist_coeffs)
scaled = cv2.resize(image_optim, None, fx=0.5, fy=0.5)
cv2.imshow("Undistorted Image", scaled)
cv2.waitKey(0)
cv2.destroyAllWindows()
