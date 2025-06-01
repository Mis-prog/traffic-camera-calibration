# from skimage import feature, transform, color, io, filters
# import numpy as np
# import matplotlib.pyplot as plt
#
# # === 1. Загрузка и grayscale ===
# image = io.imread("../../example/pushkin_aksakov/image/undistort_opencv.png")
# gray = color.rgb2gray(image)
#
# # === 2. Градиенты Sobel ===
# gx = filters.sobel_h(gray)
# gy = filters.sobel_v(gray)
# magnitude = np.hypot(gx, gy)
# orientation = np.arctan2(gy, gx)
#
# # === 3. Край по Канни ===
# edges = feature.canny(gray, sigma=2.0)
#
# # === Hough параметры ===
# thetas = np.deg2rad(np.linspace(-90, 90, 180))
# diag_len = int(np.hypot(*gray.shape))  # длина диагонали
# rhos = np.linspace(-diag_len, diag_len, 2 * diag_len)
# accumulator = np.zeros((len(rhos), len(thetas)), dtype=np.float32)

# # === Голосование с учётом ориентации ===
# delta = np.deg2rad(10)  # допустимое отклонение по направлению
#
# y_idxs, x_idxs = np.nonzero(edges)
# for x, y in zip(x_idxs, y_idxs):
#     theta_grad = orientation[y, x] + np.pi / 2  # ортогонально градиенту
#     theta_grad = (theta_grad + np.pi) % np.pi - np.pi / 2  # нормализуем в [-π/2, π/2]
#
#     for j, theta in enumerate(thetas):
#         if abs(((theta - theta_grad + np.pi) % np.pi) - np.pi / 2) < delta:
#             rho = x * np.cos(theta) + y * np.sin(theta)
#             i = int((rho + diag_len) * (len(rhos) - 1) / (2 * diag_len))
#             if 0 <= i < len(rhos):
#                 accumulator[i, j] += 1
#
#
# # === Пики ===
# from skimage.transform import hough_line_peaks
# hspace = accumulator
# angles = thetas
# dists = rhos
# accum, theta_peaks, rho_peaks = hough_line_peaks(hspace, angles, dists, threshold=0.3 * np.max(hspace))
#
#
# # === Визуализация ===
# fig, ax = plt.subplots(1, 2, figsize=(16, 8))
#
# ax[0].imshow(accumulator, extent=(np.rad2deg(thetas[0]), np.rad2deg(thetas[-1]), rhos[-1], rhos[0]), cmap='gray')
# ax[0].set_title("Hough Accumulator (с учётом ориентации)")
# ax[0].set_xlabel("θ (deg)")
# ax[0].set_ylabel("ρ (pixels)")
#
# ax[1].imshow(image)
# for angle, dist in zip(theta_peaks, rho_peaks):
#     y0 = (dist - 0 * np.cos(angle)) / np.sin(angle)
#     y1 = (dist - image.shape[1] * np.cos(angle)) / np.sin(angle)
#     ax[1].plot((0, image.shape[1]), (y0, y1), '-r', linewidth=2)
# ax[1].set_xlim((0, image.shape[1]))
# ax[1].set_ylim((image.shape[0], 0))
# ax[1].set_title("Прямые с учётом ориентации градиента")
# ax[1].axis("off")
#
# plt.tight_layout()
# plt.show()


import sys

sys.path.append(r"D:\Final qualifying work\Main\source\distortion\cpp\build\Release")

import mymodule
math = mymodule.MyMath()

print(math.mul(10,1))