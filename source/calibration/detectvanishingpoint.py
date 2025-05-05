import numpy as np
import cv2
import matplotlib.pyplot as plt


class VanishingPointDetector:
    def __init__(self):
        pass

    def detect(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)  # Преобразуем в градации серого
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=7)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=7)
        magnitude = cv2.magnitude(sobelx, sobely)
        phase = cv2.phase(sobelx, sobely, angleInDegrees=True)
        return magnitude, phase


# Загружаем изображение
image = cv2.imread("../../example/pushkin_aksakov/image/crossroads.jpg")
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

scale = 0.5  # или 0.3
image = cv2.resize(image, (0, 0), fx=scale, fy=scale)

# Детектор
point = VanishingPointDetector()
magnitude, phase = point.detect(image)

# Визуализация
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.title("Gradient Magnitude")
plt.imshow(magnitude, cmap='gray')
plt.axis("off")

plt.subplot(1, 2, 2)
plt.title("Gradient Phase (degrees)")
plt.imshow(phase, cmap='hsv')
plt.axis("off")

plt.show()


# 1. Создаём маску для сильных градиентов (берём верхние 10%)
threshold = np.percentile(magnitude, 90)
mask = magnitude > threshold

# 2. Получаем координаты этих точек и соответствующие фазы (углы)
strong_coords = np.argwhere(mask)  # массив [(y1, x1), (y2, x2), ...]
strong_phases = phase[mask]        # соответствующие углы

# 3. Визуализируем эти направления на изображении
plt.figure(figsize=(10, 10))
plt.imshow(image_rgb)
for (y, x), angle in zip(strong_coords, strong_phases):
    theta = np.deg2rad(angle)
    dx = np.cos(theta)
    dy = np.sin(theta)
    plt.arrow(x, y, dx * 10, dy * 10, color='yellow', head_width=1.5, head_length=3)

plt.title("Сильные градиенты с направлениями")
plt.axis("off")
plt.show()
