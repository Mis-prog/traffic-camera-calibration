from skimage import feature, transform, color, io, filters
import numpy as np
import matplotlib.pyplot as plt

# === 1. Загрузка и grayscale ===
image = io.imread("../../example/pushkin_aksakov/image/undistort_opencv.png")
gray = color.rgb2gray(image)

# === 2. Градиенты Sobel ===
gx = filters.sobel_h(gray)
gy = filters.sobel_v(gray)
magnitude = np.hypot(gx, gy)
orientation = np.arctan2(gy, gx)

# === 3. Край по Канни ===
edges = feature.canny(gray, sigma=2.0).astype(np.uint8)

# === Hough параметры ===
thetas = np.deg2rad(np.linspace(-90, 90, 180))
diag_len = int(np.hypot(*gray.shape))  # длина диагонали
rhos = np.linspace(-diag_len, diag_len, 2 * diag_len)
accumulator = np.zeros((len(rhos), len(thetas)), dtype=np.float32)

import sys
import os

module_dir = os.path.join(os.path.dirname(__file__), 'cpp', 'build', 'Release')
sys.path.append(module_dir)

import mymodule

accumulator = mymodule.hough_transform_with_orientation(
    edges, orientation, angle_resolution_deg=1.0, rho_resolution=1.0
)

from skimage.feature import peak_local_max
peaks = peak_local_max(accumulator, num_peaks=20, threshold_abs=50)

diag_len = int(np.hypot(*gray.shape))
angle_res = 1.0  # должно совпадать с тем, что ты подал
rho_res = 1.0

for r_idx, t_idx in peaks:
    theta = np.deg2rad(t_idx * angle_res - 90)  # от -90 до 90
    rho = r_idx * rho_res - diag_len

    a = np.cos(theta)
    b = np.sin(theta)
    x0 = a * rho
    y0 = b * rho
    x1 = int(x0 + 1000 * (-b))
    y1 = int(y0 + 1000 * (a))
    x2 = int(x0 - 1000 * (-b))
    y2 = int(y0 - 1000 * (a))

    # Нарисовать на изображении
    plt.plot([x1, x2], [y1, y2], 'r')

plt.imshow(gray, cmap='gray')
plt.title("Detected Lines")
plt.axis('off')
plt.show()