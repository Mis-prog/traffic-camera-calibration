import numpy as np
from scipy.optimize import minimize
from scipy.ndimage import map_coordinates
import cv2


def compute_r2(image_shape):
    h, w = image_shape[:2]
    r1 = np.sqrt((w / 2) ** 2 + (h / 2) ** 2)
    return r1 / 2


def denormalize_p_to_k(p1, p2, r2):
    k1 = (p1 - 16 * p2) / (-12 * r2 ** 2)
    k2 = (4 * p2 - p1) / (-12 * r2 ** 4)
    return k1, k2


def normalize_k_to_p(k1, k2, r2):
    p1 = k1 * 4 * r2 ** 2 + k2 * 16 * r2 ** 4
    p2 = k1 * r2 ** 2 + k2 * r2 ** 4
    return p1, p2


def distort_radial_norm(xy, k1, k2, cx, cy):
    """
    Применяет радиальную дисторсию к точкам в изображении.
    xy — массив точек (N, 2)
    cx, cy — центр дисторсии (обычно центр изображения)
    """
    dx = xy[:, 0] - cx
    dy = xy[:, 1] - cy
    r2 = dx ** 2 + dy ** 2
    L = 1 + k1 * r2 + k2 * r2 ** 2
    x_corr = cx + dx * L
    y_corr = cy + dy * L
    return np.stack([x_corr, y_corr], axis=1)


def undistort_point_iterative(xy, k1, k2, cx, cy, max_iter=5):
    """
    Простая итеративная процедура удаления радиальной дисторсии.
    """
    x = (xy[:, 0] - cx).copy()
    y = (xy[:, 1] - cy).copy()

    for _ in range(max_iter):
        r2 = x ** 2 + y ** 2
        L = 1 + k1 * r2 + k2 * r2 ** 2
        x = (xy[:, 0] - cx) / L
        y = (xy[:, 1] - cy) / L

    return np.stack([x + cx, y + cy], axis=1)


def curve_residuals(curves_undistorted):
    total_error = 0
    for curve in curves_undistorted:
        if len(curve) < 2:
            continue
        curve = np.array(curve)
        fit = np.polyfit(curve[:, 0], curve[:, 1], 1)
        y_fit = np.polyval(fit, curve[:, 0])
        error = np.mean((curve[:, 1] - y_fit) ** 2)
        total_error += error
    return total_error


def objective(params, curves, image_shape, r2):
    p1, p2 = params
    k1, k2 = denormalize_p_to_k(p1, p2, r2)
    cx, cy = image_shape[1] / 2, image_shape[0] / 2

    undistorted_curves = []
    for curve in curves:
        pts = np.array(curve)
        undistorted = undistort_point_iterative(pts, k1, k2, cx, cy)
        undistorted_curves.append(undistorted)

    return curve_residuals(undistorted_curves)


# === Загрузка ===
curves = np.load("clicked_curves.npy", allow_pickle=True)
image_shape = (1080, 1920)
r2 = compute_r2(image_shape)

# === Оптимизация ===
result = minimize(
    fun=objective,
    x0=np.array([0.0, 0.0]),
    args=(curves, image_shape, r2),
    method="Nelder-Mead",
    bounds=[(-1.0, 1.0), (-1.0, 1.0)]
)

print("🎯 Результат:", result)
print(result.x)

import matplotlib.pyplot as plt

plt.figure(figsize=(10, 8))
for curve in curves:
    curve = np.array(curve)
    if len(curve) < 2:
        continue
    plt.plot(curve[:, 0], curve[:, 1])
plt.gca().invert_yaxis()  # потому что координаты изображения сверху вниз
plt.axis("equal")
plt.grid(True)
plt.title("Выделенные кривые")
plt.show()
