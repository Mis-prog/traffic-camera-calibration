import sys
import json
import hashlib
import colorsys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QFileDialog,
    QVBoxLayout, QHBoxLayout, QComboBox, QWidget
)
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QFont
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QMouseEvent

from PyQt5.QtGui import QColor

PALETTE = [
    "#e6194b",  # насыщенный красный
    "#3cb44b",  # яркий зелёный
    "#ffe119",  # яркий жёлтый
    "#4363d8",  # глубокий синий
    "#f58231",  # оранжевый
    "#911eb4",  # фиолетовый
    "#00ced1",  # насыщенный бирюзовый
    "#f032e6",  # фуксия
    "#aaff00",  # ядовито-салатовый
    "#ff1493",  # тёмно-розовый
    "#008080",  # тёмная бирюза
    "#6a5acd",  # индиго
    "#8b4513",  # насыщенный коричневый
    "#ff4500",  # красно-оранжевый
    "#800000",  # бордовый
    "#00ff7f",  # неоново-зелёный
    "#808000",  # оливковый
    "#ff8c00",  # тёмно-оранжевый
    "#00008b",  # тёмно-синий
    "#000000",  # чёрный
]


class AnnotationTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Annotation Tool")

        # Виджеты
        self.image_label = QLabel()
        self.image_label.setMouseTracking(True)
        self.image_label.mousePressEvent = self.mouse_press_event
        self.image_label.mouseMoveEvent = self.mouse_move_event
        self.image_label.mouseReleaseEvent = self.mouse_release_event

        self.load_btn = QPushButton("Загрузить изображение")
        self.load_btn.clicked.connect(self.load_image)

        self.save_btn = QPushButton("Сохранить аннотации")
        self.save_btn.clicked.connect(self.save_annotations)

        self.load_ann_btn = QPushButton("Загрузить аннотации")
        self.load_ann_btn.clicked.connect(self.load_annotations)

        self.mode_selector = QComboBox()
        self.mode_selector.addItem("Точка", "point")
        self.mode_selector.addItem("Линия", "line")
        self.mode_selector.addItem("Кривая", "curve")
        self.mode_selector.currentIndexChanged.connect(self.toggle_gps_fields)

        self.class_selector = QComboBox()
        self.class_selector.setEditable(True)
        self.class_selector.addItem("all")
        self.class_selector.addItem("default")

        from PyQt5.QtWidgets import QLineEdit

        self.gps_input_1 = QLineEdit()
        self.gps_input_1.setPlaceholderText("GPS 1: широта, долгота")
        self.gps_input_2 = QLineEdit()
        self.gps_input_2.setPlaceholderText("GPS 2: широта, долгота")
        self.gps_input_2.hide()  # По умолчанию скрыто

        self.add_class_btn = QPushButton("Добавить класс")
        self.add_class_btn.clicked.connect(self.add_class)

        # Layout
        top_bar = QHBoxLayout()
        for widget in [self.load_btn, self.load_ann_btn, self.save_btn,
                       self.mode_selector, self.class_selector]:
            top_bar.addWidget(widget)

        layout = QVBoxLayout()
        layout.addLayout(top_bar)

        gps_layout = QHBoxLayout()

        self.gps_status = QLabel("Ничего не выбрано")
        layout.addWidget(self.gps_status)  # добавляется ПЕРЕД gps_layout

        gps_layout.addWidget(self.gps_input_1)
        gps_layout.addWidget(self.gps_input_2)

        self.update_gps_btn = QPushButton("Обновить GPS")
        self.update_gps_btn.clicked.connect(self.update_selected_gps)
        gps_layout.addWidget(self.update_gps_btn)

        self.clear_gps_btn = QPushButton("Сбросить GPS")
        self.clear_gps_btn.clicked.connect(self.clear_gps)
        gps_layout.addWidget(self.clear_gps_btn)

        layout.addLayout(gps_layout)

        layout.addWidget(self.image_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Логика
        self.image = None
        self.scaled_image = None
        self.display_scale = 1.0
        self.annotations = {"point": {}, "line": {}, "curve": {}}
        self.current_line = []
        self.selected = None
        self.dragging = False
        self.hover = None
        self.current_curve = []

        self.highlighted_line = None

        gps_layout.addWidget(self.update_gps_btn)

    def auto_update_gps(self):
        if self.selected:
            self.update_selected_gps()

    def clear_gps(self):
        if not self.selected:
            # Если ничего не выделено, просто очищаем поля ввода
            self.gps_input_1.clear()
            self.gps_input_2.clear()
            return

        # Очищаем поля ввода
        self.gps_input_1.clear()
        self.gps_input_2.clear()

        # Обновляем GPS выделенного объекта
        self.update_selected_gps()

    def update_selected_gps(self):
        if not self.selected:
            return

        kind, cls, item_idx, pt_idx = self.selected
        ann = self.annotations[kind][cls][item_idx]

        gps1_text = self.gps_input_1.text().strip()
        gps2_text = self.gps_input_2.text().strip()

        # Парсим GPS или устанавливаем None для пустых строк
        gps1 = self.parse_gps(gps1_text) if gps1_text else None
        gps2 = self.parse_gps(gps2_text) if gps2_text else None

        if kind == "point":
            ann["gps"] = gps1

        elif kind == "line":
            # Инициализируем массив GPS если его нет
            if "gps" not in ann:
                ann["gps"] = [None, None]
            elif not isinstance(ann["gps"], list):
                ann["gps"] = [None, None]
            elif len(ann["gps"]) < 2:
                ann["gps"] = ann["gps"] + [None] * (2 - len(ann["gps"]))

            ann["gps"][0] = gps1
            ann["gps"][1] = gps2

        elif kind == "curve":
            if gps1 is not None:
                ann["gps"] = [gps1] * len(ann["image"])
            else:
                ann["gps"] = [None] * len(ann["image"])

        print(f"GPS после обновления для {kind} класса '{cls}' №{item_idx}:", ann.get("gps"))

        # НЕ сбрасываем выделение, чтобы пользователь видел результат
        self.update_display()

    def toggle_gps_fields(self):
        mode = self.mode_selector.currentData()
        if mode == "line":
            self.gps_input_2.show()
        else:
            self.gps_input_2.hide()

    def parse_gps(self, text):
        try:
            lat_str, lon_str = text.split(",")
            return float(lat_str.strip()), float(lon_str.strip())
        except:
            return None

    def load_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение")
        if not path:
            return
        self.image = QPixmap(path)
        self.update_scale()
        self.update_display()

    def update_scale(self):
        max_width = 1280
        if self.image.width() > max_width:
            self.display_scale = max_width / self.image.width()
            self.scaled_image = self.image.scaledToWidth(max_width, Qt.SmoothTransformation)
        else:
            self.display_scale = 1.0
            self.scaled_image = self.image

    def get_mouse_pos(self, event):
        x = event.pos().x() / self.display_scale
        y = event.pos().y() / self.display_scale
        return int(x), int(y)

    def mouse_press_event(self, event):
        if not self.image:
            return

        x, y = self.get_mouse_pos(event)
        cls = self.class_selector.currentText().strip()
        mode = self.mode_selector.currentData()

        gps1_text = self.gps_input_1.text().strip()
        gps2_text = self.gps_input_2.text().strip()
        gps1 = self.parse_gps(gps1_text) if gps1_text else None
        gps2 = self.parse_gps(gps2_text) if gps2_text else None

        if cls and self.class_selector.findText(cls) == -1:
            self.class_selector.addItem(cls)

        # ПКМ — удаление точки
        if event.button() == Qt.RightButton:
            self.try_delete_nearest(x, y)
            return

        # Наведение и редактирование
        # Наведение и редактирование
        if event.button() == Qt.LeftButton:
            target = self.find_nearest_point(x, y)
            if target:
                kind, cls, item_idx, pt_idx = target
                ann = self.annotations[kind][cls][item_idx]
                self.selected = target
                self.dragging = True
                self.gps_status.setText(f"Редактируется {kind.upper()} – класс '{cls}' №{item_idx}")

                self.gps_input_1.setText("")
                self.gps_input_2.setText("")

                if kind == "line":
                    self.highlighted_line = (cls, item_idx)
                else:
                    self.highlighted_line = None

                # Автозаполнение GPS
                if kind == "point" and ann.get("gps"):
                    lat, lon = ann["gps"]
                    self.gps_input_1.setText(f"{lat:.6f}, {lon:.6f}")

                elif kind == "line" and ann.get("gps"):
                    gps_list = ann["gps"]
                    if gps_list and len(gps_list) >= 2:
                        if gps_list[0]:
                            lat1, lon1 = gps_list[0]
                            self.gps_input_1.setText(f"{lat1:.6f}, {lon1:.6f}")
                        if gps_list[1]:
                            lat2, lon2 = gps_list[1]
                            self.gps_input_2.setText(f"{lat2:.6f}, {lon2:.6f}")
                return
            else:
                self.selected = None
                self.highlighted_line = None
                self.gps_status.setText("Ничего не выбрано")
                self.update_display()

        # === Добавление новой точки/линии/кривой ===

        if mode == "point":
            self.annotations["point"].setdefault(cls, []).append({
                "image": (x, y),
                "gps": gps1
            })

        elif mode == "line":
            self.current_line.append((x, y))
            if len(self.current_line) == 2:
                self.annotations["line"].setdefault(cls, []).append({
                    "image": self.current_line.copy(),
                    "gps": [gps1, gps2]
                })
                self.current_line.clear()

        elif mode == "curve":
            self.current_curve.append((x, y))
            if event.type() == QMouseEvent.MouseButtonDblClick and len(self.current_curve) >= 2:
                gps_list = [gps1] * len(self.current_curve) if gps1 else [None] * len(self.current_curve)
                self.annotations["curve"].setdefault(cls, []).append({
                    "image": self.current_curve.copy(),
                    "gps": gps_list
                })
                self.current_curve.clear()

        self.update_display()

    def mouse_move_event(self, event):
        x, y = self.get_mouse_pos(event)

        if self.dragging and self.selected:
            kind, cls, item, pt_idx = self.selected
            try:
                if kind == "point":
                    self.annotations["point"][cls][item]["image"] = (x, y)
                elif kind == "line":
                    self.annotations["line"][cls][item]["image"][pt_idx] = (x, y)
                elif kind == "curve":
                    self.annotations["curve"][cls][item]["image"][pt_idx] = (x, y)
            except (KeyError, IndexError):
                # Например, точка была удалена
                self.dragging = False
                self.selected = None
        else:
            self.hover = self.find_nearest_point(x, y)

        self.update_display()

    def mouse_release_event(self, event):
        self.dragging = False
        # self.selected = None
        self.highlighted_line = None

    def try_delete_nearest(self, x, y, threshold=10):
        target = self.find_nearest_point(x, y, threshold)
        if not target:
            return

        kind, cls, item_idx, pt_idx = target

        if kind == "point":
            del self.annotations["point"][cls][item_idx]
            if not self.annotations["point"][cls]:
                del self.annotations["point"][cls]

        elif kind == "line":
            del self.annotations["line"][cls][item_idx]
            if not self.annotations["line"][cls]:
                del self.annotations["line"][cls]



        elif kind == "curve":

            ann = self.annotations["curve"][cls][item_idx]

            if "image" in ann and 0 <= pt_idx < len(ann["image"]):

                # Удаляем точку по индексу

                del ann["image"][pt_idx]

                # Если есть gps — тоже удаляем соответствующую

                if "gps" in ann and len(ann["gps"]) > pt_idx:
                    del ann["gps"][pt_idx]

                # Если после удаления осталось меньше 2 точек — удаляем всю кривую

                if len(ann["image"]) < 2:
                    del self.annotations["curve"][cls][item_idx]

                # Если класс стал пустой — удаляем ключ

                if not self.annotations["curve"][cls]:
                    del self.annotations["curve"][cls]

        self.hover = None
        self.selected = None
        self.update_display()

    def find_nearest_point(self, x, y, threshold=10):
        for kind in ["point", "line", "curve"]:
            for cls, items in self.annotations[kind].items():
                for i, ann in enumerate(items):
                    item = ann["image"]
                    if kind == "point":
                        px, py = item
                        if abs(px - x) < threshold and abs(py - y) < threshold:
                            return (kind, cls, i, 0)
                    elif kind == "line":
                        for j, (px, py) in enumerate(item):
                            if abs(px - x) < threshold and abs(py - y) < threshold:
                                return (kind, cls, i, j)
                    elif kind == "curve":
                        for j, (px, py) in enumerate(item):
                            if abs(px - x) < threshold and abs(py - y) < threshold:
                                return (kind, cls, i, j)
        return None

    def get_color(self, name):
        h = int(hashlib.md5(name.encode()).hexdigest(), 16)
        color_hex = PALETTE[h % len(PALETTE)]
        return QColor(color_hex)

    def update_display(self):
        if not self.image:
            return

        selected_cls = self.class_selector.currentText().strip()

        pix = QPixmap(self.scaled_image)
        painter = QPainter(pix)
        painter.setFont(QFont("Arial", 10))

        for kind in ["point", "line", "curve"]:
            for cls, items in self.annotations[kind].items():
                if selected_cls != "all" and cls != selected_cls:
                    continue
                color = self.get_color(cls)
                for i, ann in enumerate(items):
                    item = ann["image"]
                    gps = ann.get("gps", None)

                    if kind == "point":
                        x, y = [int(p * self.display_scale) for p in item]
                        pen = QPen(QColor("yellow") if self.hover == (kind, cls, i, 0) else color, 4)
                        painter.setPen(pen)
                        painter.drawEllipse(QPoint(x, y), 5, 5)
                        painter.drawText(x + 8, y - 8, cls)

                        # Отображение GPS для точки
                        if gps and isinstance(gps, (list, tuple)) and len(gps) == 2:
                            if isinstance(gps[0], (int, float)) and isinstance(gps[1], (int, float)):
                                painter.setPen(QPen(color, 1))
                                painter.drawText(x + 8, y + 12, f"{gps[0]:.6f}, {gps[1]:.6f}")

                    elif kind == "line":
                        (x1, y1), (x2, y2) = item
                        sx1, sy1 = int(x1 * self.display_scale), int(y1 * self.display_scale)
                        sx2, sy2 = int(x2 * self.display_scale), int(y2 * self.display_scale)

                        # Подсветка если выделена
                        is_selected = (self.highlighted_line == (cls, i))
                        line_pen = QPen(QColor("yellow") if is_selected else color, 6 if is_selected else 4)
                        painter.setPen(line_pen)
                        painter.drawLine(QPoint(sx1, sy1), QPoint(sx2, sy2))

                        # Точки A и B
                        for j, (px, py) in enumerate(item):
                            sx, sy = int(px * self.display_scale), int(py * self.display_scale)

                            if is_selected:
                                if j == 0:
                                    painter.setPen(QPen(QColor("limegreen"), 6))
                                    painter.setBrush(QColor("limegreen"))
                                    painter.drawEllipse(QPoint(sx, sy), 6, 6)
                                    painter.setPen(QPen(QColor("black"), 1))
                                    painter.drawText(sx + 8, sy - 8, "A")
                                elif j == 1:
                                    painter.setPen(QPen(QColor("red"), 6))
                                    painter.setBrush(QColor("red"))
                                    painter.drawEllipse(QPoint(sx, sy), 6, 6)
                                    painter.setPen(QPen(QColor("black"), 1))
                                    painter.drawText(sx + 8, sy - 8, "B")
                            else:
                                is_hover = self.hover == (kind, cls, i, j)
                                painter.setPen(QPen(QColor("yellow") if is_hover else color, 3))
                                painter.drawEllipse(QPoint(sx, sy), 4, 4)

                        # Подпись класса в центре
                        mx = int((x1 + x2) / 2 * self.display_scale)
                        my = int((y1 + y2) / 2 * self.display_scale)
                        painter.setPen(QPen(color, 1))
                        painter.drawText(mx + 6, my - 6, cls)

                        # ИСПРАВЛЕННОЕ отображение GPS координат
                        if gps and isinstance(gps, list) and len(gps) >= 2:
                            # GPS для первой точки (A)
                            if gps[0] is not None and isinstance(gps[0], (list, tuple)) and len(gps[0]) == 2:
                                painter.setPen(QPen(color, 1))
                                painter.drawText(sx1 + 8, sy1 + 12, f"{gps[0][0]:.6f}, {gps[0][1]:.6f}")

                            # GPS для второй точки (B)
                            if gps[1] is not None and isinstance(gps[1], (list, tuple)) and len(gps[1]) == 2:
                                painter.setPen(QPen(color, 1))
                                painter.drawText(sx2 + 8, sy2 + 12, f"{gps[1][0]:.6f}, {gps[1][1]:.6f}")

                    elif kind == "curve":
                        path = item
                        # Точки
                        for k, (px, py) in enumerate(path):
                            sx, sy = int(px * self.display_scale), int(py * self.display_scale)
                            is_hover = self.hover == (kind, cls, i, k)
                            pen = QPen(QColor("yellow") if is_hover else color, 4)
                            painter.setPen(pen)
                            painter.drawEllipse(QPoint(sx, sy), 4, 4)
                        # Линии
                        for k in range(1, len(path)):
                            x1, y1 = [int(p * self.display_scale) for p in path[k - 1]]
                            x2, y2 = [int(p * self.display_scale) for p in path[k]]
                            painter.setPen(QPen(color, 2))
                            painter.drawLine(QPoint(x1, y1), QPoint(x2, y2))
                        # Подпись
                        if path:
                            mx = sum(p[0] for p in path) / len(path)
                            my = sum(p[1] for p in path) / len(path)
                            painter.setPen(QPen(color, 1))
                            painter.drawText(int(mx * self.display_scale + 6),
                                             int(my * self.display_scale - 6), cls)

        # Временная линия
        if len(self.current_line) == 1:
            cx, cy = [int(p * self.display_scale) for p in self.current_line[0]]
            painter.setPen(QPen(QColor("blue"), 2))
            painter.drawEllipse(QPoint(cx, cy), 5, 5)

        # Временная кривая
        if self.current_curve:
            painter.setPen(QPen(QColor("blue"), 2))
            for k in range(1, len(self.current_curve)):
                x1, y1 = [int(p * self.display_scale) for p in self.current_curve[k - 1]]
                x2, y2 = [int(p * self.display_scale) for p in self.current_curve[k]]
                painter.drawLine(QPoint(x1, y1), QPoint(x2, y2))
            for (px, py) in self.current_curve:
                sx, sy = int(px * self.display_scale), int(py * self.display_scale)
                painter.drawEllipse(QPoint(sx, sy), 4, 4)

        painter.end()
        self.image_label.setPixmap(pix)

    def save_annotations(self):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить аннотации", "", "JSON (*.json)")
        if not path:
            return
        with open(path, "w") as f:
            json.dump(self.annotations, f, indent=2)

    def load_annotations(self):
        path, _ = QFileDialog.getOpenFileName(self, "Загрузить аннотации", "", "JSON (*.json)")
        if not path:
            return
        with open(path, "r") as f:
            self.annotations = json.load(f)

        # Гарантировать структуру
        for key in ["point", "line", "curve"]:
            if key not in self.annotations:
                self.annotations[key] = {}

        # Очистить пустые/битые кривые
        for cls in list(self.annotations["curve"].keys()):
            valid = []
            for ann in self.annotations["curve"][cls]:
                if (
                        isinstance(ann, dict) and
                        "image" in ann and
                        isinstance(ann["image"], list) and
                        len(ann["image"]) >= 2 and
                        all(isinstance(pt, (list, tuple)) and len(pt) == 2 for pt in ann["image"])
                ):
                    valid.append(ann)
            if valid:
                self.annotations["curve"][cls] = valid
            else:
                del self.annotations["curve"][cls]

        self.update_display()

        self.class_selector.clear()
        self.class_selector.addItem("all")
        known_classes = set()
        for kind in ["point", "line", "curve"]:
            for cls in self.annotations.get(kind, {}).keys():
                known_classes.add(cls)
        for cls in sorted(known_classes):
            self.class_selector.addItem(cls)

    def add_class(self):
        cls = self.class_selector.currentText().strip()
        if cls and self.class_selector.findText(cls) == -1:
            self.class_selector.addItem(cls)
        self.class_selector.setCurrentText(cls)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    tool = AnnotationTool()
    tool.show()
    sys.exit(app.exec_())
