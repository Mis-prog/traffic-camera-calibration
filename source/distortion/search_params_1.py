import matplotlib.pyplot as plt

import sys
import os

# Путь к папке, где лежит canny.pyd
module_dir = r"D:\Final qualifying work\Main\source\distortion\cmake-build-debug\extended_hough_transform"
sys.path.insert(0, module_dir)

import ami
import imageio.v3 as iio
import numpy as np

# Путь до изображения

from PIL import Image

img_path = "test/screenshot_1749312396624.jpg"
img = Image.open(img_path)
img.save("test/crossroads.png")

img_path = "test/crossroads.png"

# Получаем размеры оригинала
image = iio.imread(img_path)
height, width = image.shape[:2]

# Запускаем Canny
points = ami.run_canny(img_path, 0.5, 0.7)
xs, ys, dxs, dys = zip(*points) if points else ([], [], [], [])

res = ami.run_hough(
    xs, ys, dxs, dys,
    width=width, height=height,
    distance_point_line_max=3.0,
    max_lines=30,
    initial_distortion_param=0,
    final_distortion_param=2,
    angle_point_orientation_max_diff=3
)

print("Best param:", res["best_param"])

plt.imshow(res["accumulator"], cmap='hot')
plt.title("Accumulator")
plt.colorbar()
plt.show()

fig, ax = plt.subplots(figsize=(10, 8))
ax.imshow(image)

# Рисуем линии
for line in res["lines"]:
    a, b, c = line["a"], line["b"], line["c"]

    # Прямая: ax + by + c = 0
    # Чтобы отрисовать её, найдём две точки по краям изображения:
    x_vals = np.array([0, image.shape[1]])
    if abs(b) > 1e-6:
        y_vals = -(a * x_vals + c) / b
    else:
        # Вертикальная линия
        x_vals = np.full(2, -c / a) if abs(a) > 1e-6 else np.array([0, 0])
        y_vals = np.array([0, image.shape[0]])

    ax.plot(x_vals, y_vals, 'r-', linewidth=1.5)

# Можно также нарисовать точки, если хочешь:
for line in res["lines"]:
    for x, y in line["points"]:
        ax.plot(x, y, 'go', markersize=2)

ax.set_title(f"Best distortion param: {res['best_param']:.4f}")
plt.axis("off")
plt.tight_layout()
plt.show()

# # Устанавливаем размер в дюймах = пиксели / DPI (чтобы сохранить 1:1)
# dpi = 100  # или 96 для Windows
# figsize = (width / dpi, height / dpi)
#
# # Создаём фигуру
# fig = plt.figure(figsize=figsize, dpi=dpi)
# ax = fig.add_axes([0, 0, 1, 1])  # убираем поля
#
# # Отрисовка
# ys = [height - y for y in ys]
# ax.quiver(xs, ys, dxs, dys, angles='xy', scale_units='xy', scale=1, width=0.001, color='black')
#
# # Настройки отображения
# ax.set_xlim(0, width)
# ax.set_ylim(height, 0)  # инверсия оси Y
# ax.set_xticks([])
# ax.set_yticks([])
# ax.set_aspect('equal')
#
# fig.savefig("test/canny_edges_exact.png", dpi=dpi)
#
# plt.close(fig)
