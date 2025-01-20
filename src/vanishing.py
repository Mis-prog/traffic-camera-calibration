import cv2
import numpy as np

lines_coordinates = []

# Функция для обработки кликов на изображении
def reading_points(event, x, y, flags, params): 
    global lines_coordinates
    if event == cv2.EVENT_LBUTTONDOWN:  # Изменим на EVENT_LBUTTONDOWN для корректной работы с кликами
        lines_coordinates.append((x, y))  # Добавляем координаты в список
        print(f"Point selected: ({x}, {y})")  # Выводим координаты выбранной точки

# Функция для отображения изображения и получения точек
def point_reader(img_path):     
    org_image = cv2.imread(img_path)
    # image = cv2.resize(org_image, (800, 800))  # Изменяем размер изображения для удобства
    cv2.imshow('img', org_image)
    cv2.setMouseCallback('img', reading_points)  # Используем обработчик кликов
    cv2.waitKey(0)

# Функция для вычисления точки исчезновения
def vanishing_point():
    global lines_coordinates
    if len(lines_coordinates) != 4:
        print("Four points are needed to calculate the vanishing point.")
        return
    
    x1, y1 = lines_coordinates[0]
    x2, y2 = lines_coordinates[1]
    x3, y3 = lines_coordinates[2]
    x4, y4 = lines_coordinates[3]

    # Вычисление координат точки пересечения
    intersection_x = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / ((x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4))
    intersection_y = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / ((x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4))
    
    intersection_point = (int(intersection_x), int(intersection_y))

    print(f"Vanishing point coordinates: {intersection_point}")  # Выводим координаты точки схода

def main():
    path = r"../data/scene_from_crossroads_not_dist_line.png"  # Путь к изображению
    point_reader(path)  # Чтение точек с изображения
    vanishing_point()  # Вычисление и вывод координат точки схода
    
main()
