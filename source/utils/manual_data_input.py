import cv2
import numpy as np

# Глобальные переменные для хранения линий, точек и состояния рисования
lines = []  # Список для хранения линий (каждая линия - пара точек)
current_line = []  # Текущая создаваемая линия
dragging_point = None  # (индекс_линии, индекс_точки) для перетаскивания
selected_line = None  # Индекс выбранной линии для редактирования
edit_mode = False  # Режим редактирования активен


# Функция для обработки кликов мышью
def click_event(event, x, y, flags, param):
    global lines, current_line, dragging_point, img, img_copy, selected_line, edit_mode

    # Если нажата левая кнопка мыши
    if event == cv2.EVENT_LBUTTONDOWN:
        # Если активен режим редактирования
        if edit_mode and selected_line is not None:
            # Проверяем, не начинаем ли мы перетаскивание точки в выбранной линии
            for point_idx, point in enumerate(lines[selected_line]):
                if abs(point[0] - x) < 10 and abs(point[1] - y) < 10:
                    dragging_point = (selected_line, point_idx)
                    return
        else:
            # Проверяем, не начинаем ли мы перетаскивание точки
            for line_idx, line in enumerate(lines):
                for point_idx, point in enumerate(line):
                    if abs(point[0] - x) < 10 and abs(point[1] - y) < 10:
                        dragging_point = (line_idx, point_idx)
                        return

            # Проверяем, не выбираем ли мы линию для редактирования
            for line_idx, line in enumerate(lines):
                if len(line) == 2:
                    # Проверяем, находится ли клик рядом с линией
                    dist = point_to_line_distance(line[0], line[1], (x, y))
                    if dist < 10:  # Порог расстояния
                        selected_line = line_idx
                        edit_mode = True
                        print(f"Выбрана линия #{line_idx + 1} для редактирования")
                        redraw_image()
                        return

            # Если не перетаскиваем точку и не выбираем линию, то добавляем новую точку
            if len(current_line) < 2:
                current_line.append((x, y))
                redraw_image()

                # Если линия завершена (две точки), добавляем её в список линий
                if len(current_line) == 2:
                    lines.append(current_line.copy())
                    current_line = []  # Очищаем для создания новой линии

    # Если нажата правая кнопка мыши (отмена последнего действия или выход из режима редактирования)
    elif event == cv2.EVENT_RBUTTONDOWN:
        if edit_mode:
            edit_mode = False
            selected_line = None
            print("Режим редактирования отключен")
        elif len(current_line) > 0:
            current_line.pop()
        elif len(lines) > 0:
            lines.pop()
        redraw_image()

    # Если мышь перемещается с зажатой кнопкой мыши
    elif event == cv2.EVENT_MOUSEMOVE:
        if dragging_point is not None:
            line_idx, point_idx = dragging_point
            lines[line_idx][point_idx] = (x, y)
            redraw_image()

    # Если кнопка мыши отпущена
    elif event == cv2.EVENT_LBUTTONUP:
        dragging_point = None


# Функция для расчета расстояния от точки до линии
def point_to_line_distance(line_point1, line_point2, point):
    x1, y1 = line_point1
    x2, y2 = line_point2
    x0, y0 = point

    # Вычисляем расстояние от точки до прямой
    numerator = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
    denominator = ((y2 - y1) ** 2 + (x2 - x1) ** 2) ** 0.5

    if denominator == 0:
        return ((x0 - x1) ** 2 + (y0 - y1) ** 2) ** 0.5  # Если точки совпадают, вернуть расстояние до точки

    return numerator / denominator


# Функция для перерисовки изображения
def redraw_image():
    img[:] = img_copy.copy()

    # Рисуем все сохраненные линии
    for idx, line in enumerate(lines):
        # Цвет линии меняется в зависимости от индекса (для различия)
        color = (255, 0, 0)  # Базовый цвет - синий
        if idx % 3 == 1:
            color = (0, 255, 0)  # Зеленый
        elif idx % 3 == 2:
            color = (0, 0, 255)  # Красный

        # Если эта линия выбрана для редактирования, выделяем её
        if edit_mode and idx == selected_line:
            line_thickness = 3
            point_size = 7
            # Добавляем текст "EDIT"
            if len(line) == 2:
                mid_x = (line[0][0] + line[1][0]) // 2
                mid_y = (line[0][1] + line[1][1]) // 2 - 20
                cv2.putText(img, "EDIT", (mid_x, mid_y), cv2.FONT_HERSHEY_SIMPLEX,
                            0.8, (0, 255, 255), 2)
        else:
            line_thickness = 2
            point_size = 5

        for point in line:
            cv2.circle(img, point, point_size, (0, 255, 0), -1)
        if len(line) == 2:
            cv2.line(img, line[0], line[1], color, line_thickness)
            # Добавляем номер линии рядом с ней
            mid_x = (line[0][0] + line[1][0]) // 2
            mid_y = (line[0][1] + line[1][1]) // 2
            cv2.putText(img, str(idx + 1), (mid_x, mid_y), cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (255, 255, 255), 2)

    # Рисуем текущую создаваемую линию
    for point in current_line:
        cv2.circle(img, point, 5, (0, 255, 0), -1)
    if len(current_line) == 2:
        cv2.line(img, current_line[0], current_line[1], (255, 0, 0), 2)

    # Рисуем статус режима редактирования в верхнем левом углу
    status_text = "Режим: " + ("Редактирование" if edit_mode else "Создание")
    cv2.putText(img, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                0.8, (255, 255, 255), 2)

    # Показываем изображение
    cv2.imshow("Calibration scene", img)


# Функция для удаления выбранной линии
def delete_selected_line():
    global lines, selected_line, edit_mode
    if selected_line is not None and 0 <= selected_line < len(lines):
        del lines[selected_line]
        print(f"Линия #{selected_line + 1} удалена")
        selected_line = None
        edit_mode = False
        redraw_image()


# Загружаем изображение
img = cv2.imread('../example/pushkin_aksakov/image/pattern_corrected_image.png')
if img is None:
    print("Ошибка загрузки изображения. Проверьте путь к файлу.")
    exit()

img_copy = img.copy()  # Создаем копию для перерисовки

# Отображаем изображение
cv2.namedWindow('Calibration scene', cv2.WINDOW_NORMAL)
cv2.imshow("Calibration scene", img)

# Подключаем обработчик событий
cv2.setMouseCallback("Calibration scene", click_event)

# Выводим инструкции
print("Инструкции:")
print("- Левый клик: добавить точку или начать перетаскивание существующей точки")
print("- Левый клик на линии: выбрать линию для редактирования")
print("- Правый клик: отменить последнее действие или выйти из режима редактирования")
print("- Две точки создают линию, после чего можно начать создавать следующую линию")
print("- Нажмите 'e' для переключения режима редактирования")
print("- Нажмите 'd' для удаления выбранной линии")
print("- Нажмите 's' для сохранения координат всех линий в файл")
print("- Нажмите 'q' или 'Esc' для выхода")

# Основной цикл
while True:
    key = cv2.waitKey(1) & 0xFF
    if key == 27 or key == ord('q'):  # Esc или q для выхода
        break
    elif key == ord('s'):  # 's' для сохранения
        with open('../example/pushkin_aksakov/marked_data/calibration_lines.txt', 'w') as f:
            for idx, line in enumerate(lines):
                f.write(f"Line {idx + 1}: {line}\n")
        print(f"Сохранено {len(lines)} линий в файл 'calibration_lines.txt'")
        print(lines)
    elif key == ord('e'):  # 'e' для переключения режима редактирования
        edit_mode = not edit_mode
        if not edit_mode:
            selected_line = None
        print(f"Режим редактирования {'включен' if edit_mode else 'выключен'}")
        redraw_image()
    elif key == ord('d'):  # 'd' для удаления выбранной линии
        delete_selected_line()

# Закрываем окна
cv2.destroyAllWindows()