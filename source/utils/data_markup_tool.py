import cv2
import numpy as np
import json
import os


class LineAnnotationTool:
    def __init__(self, image_path, save_dir="annotations", save_file="lines.json"):
        # Загружаем изображение и проверяем его наличие
        self.image = cv2.imread(image_path)
        if self.image is None:
            raise FileNotFoundError(f"Не удалось загрузить изображение: {image_path}")

        # Создаем копию изображения для отрисовки
        self.image_copy = self.image.copy()

        # Инициализация переменных для хранения линий и состояния
        self.lines = []
        self.current_line = []
        self.dragging_point = None
        self.selected_line = None
        self.edit_mode = False
        self.hover_point = None
        self.window_name = "Calibration scene"
        self.cursor_position = (0, 0)

        # Папка для сохранения аннотаций
        self.save_dir = save_dir
        self.save_file = save_file
        os.makedirs(self.save_dir, exist_ok=True)

    def run(self):
        # Создаем окно и настраиваем обработку мыши
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        print("Нажмите 'q' для выхода | 's' сохранить | 'd' удалить | 'e' редактировать")

        # Основной цикл взаимодействия с пользователем
        while True:
            self.redraw()
            key = cv2.waitKey(1) & 0xFF

            # Выход
            if key == 27 or key == ord('q'):
                break

            # Сохранение линий
            elif key == ord('s'):
                self.save_lines()

            # Переключение режима редактирования
            elif key == ord('e'):
                self.edit_mode = not self.edit_mode
                if not self.edit_mode:
                    self.selected_line = None
                print(f"Режим редактирования {'включен' if self.edit_mode else 'выключен'}")

            # Удаление выбранной линии
            elif key == ord('d'):
                self.delete_selected_line()

            # Отмена последней точки или линии
            elif key == 8:  # Backspace
                if self.current_line:
                    self.current_line.pop()
                elif self.lines:
                    self.lines.pop()

        # Закрытие всех окон
        cv2.destroyAllWindows()

    def mouse_callback(self, event, x, y, flags, param):
        self.cursor_position = (x, y)

        if event == cv2.EVENT_LBUTTONDOWN:
            if self.edit_mode and self.selected_line is not None:
                for point_idx, point in enumerate(self.lines[self.selected_line]):
                    if self.is_near(point, (x, y)):
                        self.dragging_point = (self.selected_line, point_idx)
                        return

            for line_idx, line in enumerate(self.lines):
                for point_idx, point in enumerate(line):
                    if self.is_near(point, (x, y)):
                        self.dragging_point = (line_idx, point_idx)
                        return

            for line_idx, line in enumerate(self.lines):
                if len(line) == 2 and self.point_to_line_distance(line[0], line[1], (x, y)) < 10:
                    self.selected_line = line_idx
                    self.edit_mode = True
                    print(f"Выбрана линия #{line_idx + 1} для редактирования")
                    return

            if len(self.current_line) < 2:
                self.current_line.append((x, y))
                if len(self.current_line) == 2 and self.current_line[0] != self.current_line[1]:
                    self.lines.append(self.current_line.copy())
                    self.current_line.clear()

        elif event == cv2.EVENT_RBUTTONDOWN:
            if self.edit_mode:
                self.edit_mode = False
                self.selected_line = None
            elif self.current_line:
                self.current_line.pop()
            elif self.lines:
                self.lines.pop()

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.dragging_point:
                line_idx, point_idx = self.dragging_point
                self.lines[line_idx][point_idx] = (x, y)
            else:
                self.hover_point = self.get_hover_point(x, y)

        elif event == cv2.EVENT_LBUTTONUP:
            self.dragging_point = None

    def redraw(self):
        img = self.image.copy()

        for idx, line in enumerate(self.lines):
            color = self.get_color(idx)
            point_size = 7 if idx == self.selected_line else 5
            thickness = 3 if idx == self.selected_line else 2

            for pt in line:
                cv2.circle(img, pt, point_size, (0, 255, 0), -1)
            if len(line) == 2:
                cv2.line(img, line[0], line[1], color, thickness)
                mid = ((line[0][0] + line[1][0]) // 2, (line[0][1] + line[1][1]) // 2)
                cv2.putText(img, f"Line {idx + 1}", mid, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                if idx == self.selected_line:
                    cv2.putText(img, "EDIT", (mid[0], mid[1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        for pt in self.current_line:
            cv2.circle(img, pt, 5, (0, 255, 0), -1)
        if len(self.current_line) == 2:
            cv2.line(img, self.current_line[0], self.current_line[1], (255, 0, 0), 2)

        if self.hover_point:
            line_idx, pt_idx = self.hover_point
            pt = self.lines[line_idx][pt_idx]
            cv2.circle(img, pt, 8, (0, 255, 255), 2)

        status = "Редактирование" if self.edit_mode else "Создание"
        cv2.putText(img, f"Режим: {status}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.imshow(self.window_name, img)

    def delete_selected_line(self):
        if self.selected_line is not None and 0 <= self.selected_line < len(self.lines):
            del self.lines[self.selected_line]
            print(f"Удалена линия #{self.selected_line + 1}")
            self.selected_line = None
            self.edit_mode = False

    def save_lines(self):
        # Формируем путь и сохраняем в JSON
        filename = os.path.join(self.save_dir, self.save_file)
        data = {f"Line {i + 1}": line for i, line in enumerate(self.lines)}
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Сохранено {len(self.lines)} линий в файл: {filename}")

    @staticmethod
    def is_near(p1, p2, threshold=10):
        return abs(p1[0] - p2[0]) < threshold and abs(p1[1] - p2[1]) < threshold

    @staticmethod
    def point_to_line_distance(p1, p2, p0):
        x1, y1 = p1
        x2, y2 = p2
        x0, y0 = p0
        num = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
        den = np.hypot(y2 - y1, x2 - x1)
        return num / den if den else np.hypot(x0 - x1, y0 - y1)

    def get_hover_point(self, x, y):
        for i, line in enumerate(self.lines):
            for j, pt in enumerate(line):
                if self.is_near(pt, (x, y)):
                    return i, j
        return None

    @staticmethod
    def get_color(i):
        hsv = np.uint8([[[i * 20 % 180, 255, 255]]])
        bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0][0]
        return int(bgr[0]), int(bgr[1]), int(bgr[2])


if __name__ == "__main__":
    # Указываем путь к изображению для разметки
    image_path = "../../example/pushkin_aksakov/image/pattern_corrected_image.png"
    dir_path = "../../example/pushkin_aksakov/vp/"
    tool = LineAnnotationTool(image_path, dir_path, 'vp3.json')
    tool.run()
