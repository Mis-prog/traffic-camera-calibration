import cv2
import numpy as np

def create_black_square_grid(cell_size=40, num_rows=6, num_cols=8, margin=40, square_size=20):
    """
    Создаёт изображение с чёрными квадратами, равномерно размещёнными в сетке на белом фоне.

    Parameters:
        cell_size: int — расстояние между центрами квадратов
        num_rows: int — число рядов
        num_cols: int — число колонок
        margin: int — отступ от краёв изображения
        square_size: int — размер стороны чёрного квадрата

    Returns:
        np.ndarray — изображение с сеткой
    """
    height = 2 * margin + cell_size * (num_rows - 1)
    width = 2 * margin + cell_size * (num_cols - 1)

    image = np.ones((height, width, 3), dtype=np.uint8) * 255  # белый фон

    for row in range(num_rows):
        for col in range(num_cols):
            center_x = margin + col * cell_size
            center_y = margin + row * cell_size

            top_left = (center_x - square_size // 2, center_y - square_size // 2)
            bottom_right = (center_x + square_size // 2, center_y + square_size // 2)

            cv2.rectangle(image, top_left, bottom_right, color=(0, 0, 0), thickness=-1)

    return image

# # === Генерация и сохранение ===
# img = create_black_square_grid()
# cv2.imwrite("input.png", img)

import cv2
import numpy as np

def create_line_grid(cell_size=40, num_rows=6, num_cols=8, margin=40, thickness=1):
    """
    Создаёт изображение с горизонтальными и вертикальными линиями, равномерно распределёнными на белом фоне.

    Parameters:
        cell_size: int — расстояние между линиями
        num_rows: int — число ячеек по вертикали
        num_cols: int — число ячеек по горизонтали
        margin: int — отступ от краёв изображения
        thickness: int — толщина линий

    Returns:
        np.ndarray — изображение с сеткой линий
    """
    height = 2 * margin + cell_size * num_rows
    width = 2 * margin + cell_size * num_cols

    image = np.ones((height, width, 3), dtype=np.uint8) * 255  # белый фон

    # Горизонтальные линии
    for row in range(num_rows + 1):
        y = margin + row * cell_size
        cv2.line(image, (margin, y), (width - margin, y), color=(0, 0, 0), thickness=thickness)

    # Вертикальные линии
    for col in range(num_cols + 1):
        x = margin + col * cell_size
        cv2.line(image, (x, margin), (x, height - margin), color=(0, 0, 0), thickness=thickness)

    return image

# === Генерация и сохранение ===
img = create_line_grid()
cv2.imwrite("grid_lines.png", img)
