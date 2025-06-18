import cv2
import numpy as np


def distort_image_radially(image, k1, k2=0.0, k3=0.0):
    h, w = image.shape[:2]
    x_c, y_c = w / 2, h / 2

    # Сетка координат
    xv, yv = np.meshgrid(np.arange(w), np.arange(h))
    dx = xv - x_c
    dy = yv - y_c
    r2 = dx ** 2 + dy ** 2

    # Коэффициент масштабирования (L(r))
    L = 1 + k1 * r2 + k2 * r2 ** 2 + k3 * r2 ** 3
    map_x = (dx * L + x_c).astype(np.float32)
    map_y = (dy * L + y_c).astype(np.float32)

    # Интерполяция
    distorted = cv2.remap(image, map_x, map_y,
                          interpolation=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_CONSTANT,
                          borderValue=(255, 255, 255)
                          )
    return distorted


# === Загрузка и обработка ===
img = cv2.imread("grid_lines.png")  # путь к изображению

distorted = distort_image_radially(img, k1=-2e-6)

# distorted = distort_image_radially(img, k1=1.3e-5, k2=-2.5e-10)

cv2.imwrite("distorted_pinkush.png", distorted)
