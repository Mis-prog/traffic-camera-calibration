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
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
    "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
    "#bcbd22", "#17becf", "#aec7e8", "#ffbb78",
    "#98df8a", "#ff9896", "#c5b0d5", "#c49c94"
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
        gps_layout.addWidget(self.gps_input_1)
        gps_layout.addWidget(self.gps_input_2)
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

        self.update_gps_btn = QPushButton("Обновить GPS")
        self.update_gps_btn.clicked.connect(self.update_selected_gps)
        gps_layout.addWidget(self.update_gps_btn)

    def update_selected_gps(self):
        if not self.selected:
            return

        kind, cls, item_idx, pt_idx = self.selected

        if kind == "point":
            gps = self.parse_gps(self.gps_input_1.text())
            if gps:
                self.annotations["point"][cls][item_idx]["gps"] = gps

        elif kind == "line":
            gps1_new = self.parse_gps(self.gps_input_1.text())
            gps2_new = self.parse_gps(self.gps_input_2.text())

            gps_old = self.annotations["line"][cls][item_idx].get("gps", [None, None])
            if len(gps_old) != 2:
                gps_old = [None, None]

            if gps1_new:
                gps_old[0] = gps1_new
            if gps2_new:
                gps_old[1] = gps2_new

            self.annotations["line"][cls][item_idx]["gps"] = gps_old
            self.highlighted_line = (cls, item_idx)  # ❗ обновим выделение вручную

        elif kind == "curve":
            gps = self.parse_gps(self.gps_input_1.text())
            if gps:
                n = len(self.annotations["curve"][cls][item_idx]["image"])
                self.annotations["curve"][cls][item_idx]["gps"] = [gps] * n

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
        gps1 = self.parse_gps(self.gps_input_1.text())
        gps2 = self.parse_gps(self.gps_input_2.text())

        cls = self.class_selector.currentText().strip()
        mode = self.mode_selector.currentData()

        if cls and self.class_selector.findText(cls) == -1:
            self.class_selector.addItem(cls)

        # === ПКМ: удалить ===
        if event.button() == Qt.RightButton:
            self.try_delete_nearest(x, y)
            return

        # === ЛКМ: редактирование (если навёлся на точку) ===
        if event.button() == Qt.LeftButton:
            target = self.find_nearest_point(x, y)
            if target:
                kind, cls, item_idx, pt_idx = target
                ann = self.annotations[kind][cls][item_idx]
                self.selected = target
                self.dragging = True

                # 🔶 Подсветка
                if kind == "line":
                    self.highlighted_line = (cls, item_idx)
                else:
                    self.highlighted_line = None

                # 📍 GPS автозаполнение
                if kind == "point":
                    gps = ann.get("gps")
                    if gps:
                        self.gps_input_1.setText(f"{gps[0]:.6f}, {gps[1]:.6f}")

                elif kind == "line":
                    gps_list = ann.get("gps")
                    if gps_list and len(gps_list) >= 2:
                        gps1 = gps_list[0]
                        gps2 = gps_list[1]
                        if gps1:
                            self.gps_input_1.setText(f"{gps1[0]:.6f}, {gps1[1]:.6f}")
                        if gps2:
                            self.gps_input_2.setText(f"{gps2[0]:.6f}, {gps2[1]:.6f}")

                return

        # === ЛКМ: добавление точки ===
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

            if event.type() == QMouseEvent.MouseButtonDblClick:

                if len(self.current_curve) >= 2:
                    self.annotations["curve"].setdefault(cls, []).append({

                        "image": self.current_curve.copy(),

                        "gps": [gps1 for _ in self.current_curve]

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
        self.selected = None

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
            curve = self.annotations["curve"][cls][item_idx]
            if 0 <= pt_idx < len(curve):
                del curve[pt_idx]
                if len(curve) < 2:
                    del self.annotations["curve"][cls][item_idx]
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
                        if gps and isinstance(gps, (list, tuple)) and len(gps) == 2 and isinstance(gps[0],
                                                                                                   (int, float)):
                            painter.setPen(QPen(color, 1))
                            painter.drawText(x + 8, y + 12, f"{gps[0]:.6f}, {gps[1]:.6f}")




                    elif kind == "line":

                        # Получаем точки начала и конца

                        (x1, y1), (x2, y2) = item

                        sx1, sy1 = int(x1 * self.display_scale), int(y1 * self.display_scale)

                        sx2, sy2 = int(x2 * self.display_scale), int(y2 * self.display_scale)

                        # Линия

                        painter.setPen(QPen(color, 4))

                        painter.drawLine(QPoint(sx1, sy1), QPoint(sx2, sy2))

                        # Точки начала и конца

                        for j, (px, py) in enumerate(item):
                            sx, sy = int(px * self.display_scale), int(py * self.display_scale)

                            is_hover = self.hover == (kind, cls, i, j)

                            pen = QPen(QColor("yellow") if is_hover else color, 3)

                            painter.setPen(pen)

                            painter.drawEllipse(QPoint(sx, sy), 4, 4)

                        # Подпись класса в центре

                        mx = int((x1 + x2) / 2 * self.display_scale)

                        my = int((y1 + y2) / 2 * self.display_scale)

                        painter.setPen(QPen(color, 1))

                        painter.drawText(mx + 6, my - 6, cls)

                        # Подписи GPS координат у обеих точек

                        if gps and isinstance(gps, list):

                            if len(gps) >= 1 and isinstance(gps[0], (list, tuple)) and len(gps[0]) == 2:
                                painter.setPen(QPen(color, 1))

                                painter.drawText(sx1 + 8, sy1 + 12, f"{gps[0][0]:.6f}, {gps[0][1]:.6f}")

                            if len(gps) >= 2 and isinstance(gps[1], (list, tuple)) and len(gps[1]) == 2:
                                painter.setPen(QPen(color, 1))

                                painter.drawText(sx2 + 8, sy2 + 12, f"{gps[1][0]:.6f}, {gps[1][1]:.6f}")

                        # Подсветка если выделена
                        is_selected = (self.highlighted_line == (cls, i))
                        line_pen = QPen(QColor("yellow") if is_selected else color, 6 if is_selected else 4)
                        painter.setPen(line_pen)
                        painter.drawLine(QPoint(sx1, sy1), QPoint(sx2, sy2))

                        # Точки A и B
                        labels = ["A", "B"]
                        for j, (px, py) in enumerate(item):
                            sx, sy = int(px * self.display_scale), int(py * self.display_scale)

                            if is_selected:
                                if j == 0:
                                    painter.setPen(QPen(QColor("limegreen"), 6))  # Начало — зелёная
                                    painter.setBrush(QColor("limegreen"))
                                    painter.drawEllipse(QPoint(sx, sy), 6, 6)
                                    painter.setPen(QPen(QColor("black"), 1))
                                    painter.drawText(sx + 8, sy - 8, "A")
                                elif j == 1:
                                    painter.setPen(QPen(QColor("red"), 6))  # Конец — красная
                                    painter.setBrush(QColor("red"))
                                    painter.drawEllipse(QPoint(sx, sy), 6, 6)
                                    painter.setPen(QPen(QColor("black"), 1))
                                    painter.drawText(sx + 8, sy - 8, "B")
                            else:
                                is_hover = self.hover == (kind, cls, i, j)
                                painter.setPen(QPen(QColor("yellow") if is_hover else color, 3))
                                painter.drawEllipse(QPoint(sx, sy), 4, 4)



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
