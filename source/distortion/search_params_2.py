import numpy as np
import cv2
from scipy.optimize import minimize
import matplotlib.pyplot as plt


def compute_r2(image_shape):
    h, w = image_shape[:2]
    r1 = np.sqrt((w / 2) ** 2 + (h / 2) ** 2)
    return r1 / 2


def denormalize_p_to_k(p1, p2, r2):
    k1 = (p1 - 16 * p2) / (-12 * r2 ** 2)
    k2 = (4 * p2 - p1) / (-12 * r2 ** 4)
    return k1, k2


def undistort_point(xy, k1, k2, cx, cy):
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
    global cx, cy
    cx, cy = image_shape[1] / 2, image_shape[0] / 2

    undistorted_curves = []
    for curve in curves:
        pts = np.array(curve)
        undistorted = undistort_point(pts, k1, k2, cx, cy)
        undistorted_curves.append(undistorted)

    return curve_residuals(undistorted_curves)


curves = np.load("clicked_curves.npy", allow_pickle=True)[:-1]
image_shape = (1080, 1920)
r2 = compute_r2(image_shape)

result = minimize(
    fun=objective,
    x0=np.array([0.0, 0.0]),
    args=(curves, image_shape, r2),
    method="Nelder-Mead",
    bounds=[(-1.0, 1.0), (-1.0, 1.0)]
)

print(result)
print(result.x, cx, cy)

opt_p1, opt_p2 = result.x
opt_k1, opt_k2 = denormalize_p_to_k(opt_p1, opt_p2, r2)
print(opt_k1, opt_k2)

# import matplotlib.pyplot as plt
# import cv2
#
# # Загрузи изображение
# img = cv2.imread("crossroads.jpg")
# img_new = cv2.imread("undistorted_output.jpg")
# img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # для корректного отображения в matplotlib
# img_rgb_new = cv2.cvtColor(img_new, cv2.COLOR_BGR2RGB)
#
# # === Визуализация ===
# fig, axs = plt.subplots(1, 2, figsize=(14, 6))
# axs[0].set_title("До коррекции")
# axs[1].set_title("После коррекции")
#
# axs[0].imshow(img_rgb)
# axs[1].imshow(img_rgb_new)
#
# for curve in curves:
#     curve = np.array(curve)
#     if len(curve) < 2:
#         continue
#     axs[0].plot(curve[:, 0], curve[:, 1], 'ro-', linewidth=1.5)
#
#     scale = 1.5264166665503942
#     undistorted = undistort_point(curve, opt_k1, opt_k2, cx, cy)
#     undistorted_scaled = (undistorted - np.array([cx, cy])) * 1 / scale + np.array([cx, cy])
#     axs[1].plot(undistorted_scaled[:, 0], undistorted_scaled[:, 1], 'go-', linewidth=1.5)
#
# for ax in axs:
#     ax.set_xlim(0, image_shape[1])
#     ax.set_ylim(image_shape[0], 0)  # инверсия Y
#     ax.set_aspect('equal')
#     ax.axis('off')
#
# plt.tight_layout()
# plt.show()
