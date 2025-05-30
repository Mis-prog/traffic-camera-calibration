import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

points = []

# Обработчик мыши для ручного выбора кривых
def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))

def distort_point(p, k, cx, cy):
    x, y = p[0] - cx, p[1] - cy
    r2 = x**2 + y**2
    scale = 1 + k * r2
    return x * scale + cx, y * scale + cy

def undistort(points, k, cx, cy):
    return np.array([distort_point(p, -k, cx, cy) for p in points])

# Функция потерь: насколько "непрямая" линия
def loss_fn(k, original_pts, cx, cy):
    undistorted = undistort(original_pts, k, cx, cy)
    x, y = undistorted[:, 0], undistorted[:, 1]
    A = np.vstack([x, np.ones_like(x)]).T
    m, c = np.linalg.lstsq(A, y, rcond=None)[0]
    y_fit = m * x + c
    return np.mean((y - y_fit) ** 2)

# Загрузим изображение
img = cv2.imread("image/crossroads.jpg")
if img is None:
    raise FileNotFoundError("Изображение не найдено")

h, w = img.shape[:2]
cx, cy = w / 2, h / 2

cv2.imshow("Выдели линию (ESC чтобы завершить)", img)
cv2.setMouseCallback("Выдели линию (ESC чтобы завершить)", mouse_callback)

while True:
    key = cv2.waitKey(1)
    if key == 27 or len(points) > 10:  # ESC или больше 10 точек
        break

cv2.destroyAllWindows()

points = np.array(points)

# Оптимизация параметра искажения
res = minimize(loss_fn, x0=[0.0], args=(points, cx, cy), method='Nelder-Mead')
k_opt = res.x[0]
print(f"Оптимальный параметр искажения: k = {k_opt:.6f}")

# Создание сетки и коррекция изображения
map_x, map_y = np.meshgrid(np.arange(w), np.arange(h))
map_undistort = np.zeros((h, w, 2), dtype=np.float32)

for y in range(h):
    for x in range(w):
        dx, dy = x - cx, y - cy
        r2 = dx**2 + dy**2
        scale = 1 + k_opt * r2
        x_u = dx / scale + cx
        y_u = dy / scale + cy
        map_undistort[y, x] = [x_u, y_u]

undistorted = cv2.remap(img, map_undistort[..., 0], map_undistort[..., 1], cv2.INTER_LINEAR)

# Отображение результатов
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.title("Исходное изображение")
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.scatter(*zip(*points), c='red')
plt.subplot(1, 2, 2)
plt.title("После коррекции дисторсии")
plt.imshow(cv2.cvtColor(undistorted, cv2.COLOR_BGR2RGB))
plt.tight_layout()
plt.show()
