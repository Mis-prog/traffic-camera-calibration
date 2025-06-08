import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from core import Camera


def undistort_image(image, K, dist_coeffs):
    h, w = image.shape[:2]
    new_K, _ = cv2.getOptimalNewCameraMatrix(K, dist_coeffs, (w, h), alpha=1.0)
    return cv2.undistort(image, K, dist_coeffs, None, K)


def undistort_point(point, K, dist_coeffs):
    point = np.array(point, dtype=np.float32).reshape(-1, 1, 2)  # Передаем точку как массив
    undistorted_point = cv2.undistortPoints(point, K, dist_coeffs)

    # Преобразуем нормализованные координаты в пиксельные
    undistorted_point_pixels = cv2.convertPointsToHomogeneous(undistorted_point)
    undistorted_point_pixels = np.dot(undistorted_point_pixels, K.T)

    pixel_coords = undistorted_point_pixels[0, 0]
    return pixel_coords[:2]  # Возвращаем только пиксельные координаты


def curve_residuals(curves_undistorted):
    """
    Вычисляет ошибку прямолинейности для каждой кривой (сумма расстояний до наилучшей прямой).
    """
    total_error = 0
    for curve in curves_undistorted:
        if len(curve) < 2:
            continue
        curve = np.array(curve)

        # Подгоняем прямую через полиномиальную регрессию 1-й степени
        fit = np.polyfit(curve[:, 0], curve[:, 1], 1)
        y_fit = np.polyval(fit, curve[:, 0])
        error = np.mean((curve[:, 1] - y_fit) ** 2)
        total_error += error
    return total_error


def objective(k, curves):
    """
    k — это массив [k1], параметр радиальной дисторсии
    """
    dist_coeffs = np.array([k[1], k[2], 0, 0, 0], dtype=np.float32)  # только k1
    K = np.array([
        [k[0], 0, 960],
        [0, k[0], 540],
        [0, 0, 1]
    ], dtype=np.float32)
    undistorted_curves = []

    for curve in curves:
        undist = []
        for pt in curve:
            new_pt = undistort_point(pt, K, dist_coeffs)
            undist.append(new_pt)
        undistorted_curves.append(undist)

    return curve_residuals(undistorted_curves)


from scipy.optimize import minimize

# Загрузка
curves = np.load("clicked_curves.npy", allow_pickle=True)

# Оптимизация
result = minimize(
    fun=objective,
    x0=np.array([1200, 0.0, 0.0]),  # начальное значение k1
    args=(curves,),
    method="Powell",  # работает лучше без градиентов
    bounds=[(800, 2000), (-1.0, 1.0), (-1.0, 1.0)]
)

f_opt, k1_opt, k2_opt = result.x
print(f"📷 Оптимизированное фокусное расстояние f = {f_opt:.2f}")
print(f"🔧 Оптимизированное значение k1 = {k1_opt:.6f}")
print(f"🔧 Оптимизированное значение k2 = {k2_opt:.6f}")

camera = Camera("../../example/pushkin_aksakov/image/crossroads.jpg")
camera.intrinsics.set_focal_length(f_opt)
K = camera.intrinsics.get()

image = undistort_image(camera.get_image(), K, np.array([k1_opt, k2_opt, 0, 0, 0], dtype=np.float32))

import matplotlib.pyplot as plt

# Получаем выпрямленное изображение
# image = undistort_image(
#     camera.get_image(),
#     K,
#     np.array([k1_opt, k2_opt, 0, 0, 0], dtype=np.float32)
# )
#
# image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
# cv2.imwrite("../../example/pushkin_aksakov/image/undistort_opencv.png", image_bgr)