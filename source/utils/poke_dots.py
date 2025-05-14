import cv2
import numpy as np

# Список для хранения координат точек
points = []

# Функция для захвата кликов по изображению
def click_event(event, x, y, flags, param):
    global points
    # Если нажата левая кнопка мыши, сохраняем координаты точки
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        # Рисуем точку на изображении
        cv2.circle(image, (x, y), 5, (0, 0, 255), -1)
        cv2.imshow("Image with Points", image)

# Загрузка изображения
image = cv2.imread('../../example/pushkin_aksakov/image/crossroads.jpg')  # Укажи путь к своему изображению
image_copy = image.copy()

# Отображаем изображение
cv2.imshow("Image with Points", image)

# Подключаем функцию для захвата кликов
cv2.setMouseCallback("Image with Points", click_event)

# Ждем, пока пользователь не нажмет клавишу 'q' для выхода
cv2.waitKey(0)
cv2.destroyAllWindows()

# Сохраняем координаты точек в файл (например, в формате CSV)
with open("points.csv", "w") as f:
    for point in points:
        f.write(f"{point[0]},{point[1]}\n")

# Выводим сохраненные точки
print("Points saved to points.csv:")
for point in points:
    print(point)
