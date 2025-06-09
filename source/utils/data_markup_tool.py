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

        self.class_selector = QComboBox()
        self.class_selector.setEditable(True)
        self.class_selector.addItem("all")
        self.class_selector.addItem("default")

        self.add_class_btn = QPushButton("Добавить класс")
        self.add_class_btn.clicked.connect(self.add_class)

        # Layout
        top_bar = QHBoxLayout()
        for widget in [self.load_btn, self.load_ann_btn, self.save_btn,
                       self.mode_selector, self.class_selector, self.add_class_btn]:
            top_bar.addWidget(widget)

        layout = QVBoxLayout()
        layout.addLayout(top_bar)
        layout.addWidget(self.image_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Логика
        self.image = None
        self.scaled_image = None
        self.display_scale = 1.0
        self.annotations = {"point": {}, "line": {}}
        self.current_line = []
        self.selected = None
        self.dragging = False
        self.hover = None

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

        if cls and self.class_selector.findText(cls) == -1:
            self.class_selector.addItem(cls)

        if event.button() == Qt.RightButton:
            self.try_delete_nearest(x, y)
            return

        self.selected = self.find_nearest_point(x, y)
        if self.selected:
            self.dragging = True
            return

        if mode == "point":
            self.annotations["point"].setdefault(cls, []).append((x, y))
        elif mode == "line":
            self.current_line.append((x, y))
            if len(self.current_line) == 2:
                self.annotations["line"].setdefault(cls, []).append(self.current_line.copy())
                self.current_line.clear()

        self.update_display()

    def mouse_move_event(self, event):
        x, y = self.get_mouse_pos(event)
        if self.dragging and self.selected:
            kind, cls, item, pt_idx = self.selected
            if kind == "point":
                self.annotations["point"][cls][item] = (x, y)
            elif kind == "line":
                self.annotations["line"][cls][item][pt_idx] = (x, y)
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
        kind, cls, item_idx, _ = target
        del self.annotations[kind][cls][item_idx]
        if not self.annotations[kind][cls]:
            del self.annotations[kind][cls]
        self.update_display()

    def find_nearest_point(self, x, y, threshold=10):
        for kind in ["point", "line"]:
            for cls, items in self.annotations[kind].items():
                for i, item in enumerate(items):
                    if kind == "point":
                        px, py = item
                        if abs(px - x) < threshold and abs(py - y) < threshold:
                            return (kind, cls, i, 0)
                    elif kind == "line":
                        for j, (px, py) in enumerate(item):
                            if abs(px - x) < threshold and abs(py - y) < threshold:
                                return (kind, cls, i, j)
        return None

    def get_color(self, name):
        h = int(hashlib.md5(name.encode()).hexdigest(), 16)
        hue = (h % 360) / 360.0
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        return QColor(int(r * 255), int(g * 255), int(b * 255))

    def update_display(self):
        if not self.image:
            return

        selected_cls = self.class_selector.currentText().strip()
        
        pix = QPixmap(self.scaled_image)
        painter = QPainter(pix)
        painter.setFont(QFont("Arial", 10))

        for kind in ["point", "line"]:
            for cls, items in self.annotations[kind].items():
                if selected_cls != "all" and cls != selected_cls:
                    continue
                color = self.get_color(cls)
                for i, item in enumerate(items):
                    if kind == "point":
                        x, y = [int(p * self.display_scale) for p in item]
                        pen = QPen(QColor("yellow") if self.hover == (kind, cls, i, 0) else color, 4)
                        painter.setPen(pen)
                        painter.drawEllipse(QPoint(x, y), 5, 5)
                        painter.drawText(x + 8, y - 8, cls)
                    elif kind == "line":
                        for j, (px, py) in enumerate(item):
                            sx, sy = int(px * self.display_scale), int(py * self.display_scale)
                            pen = QPen(QColor("yellow") if self.hover == (kind, cls, i, j) else color, 3)
                            painter.setPen(pen)
                            painter.drawEllipse(QPoint(sx, sy), 4, 4)
                        sx1, sy1 = int(item[0][0] * self.display_scale), int(item[0][1] * self.display_scale)
                        sx2, sy2 = int(item[1][0] * self.display_scale), int(item[1][1] * self.display_scale)
                        painter.setPen(QPen(color, 4))
                        painter.drawLine(QPoint(sx1, sy1), QPoint(sx2, sy2))

                        # Центр линии и подпись класса
                        mx = int((item[0][0] + item[1][0]) / 2 * self.display_scale)
                        my = int((item[0][1] + item[1][1]) / 2 * self.display_scale)
                        painter.setPen(QPen(color, 1))
                        painter.drawText(mx + 6, my - 6, cls)

        if len(self.current_line) == 1:
            cx, cy = [int(p * self.display_scale) for p in self.current_line[0]]
            painter.setPen(QPen(QColor("blue"), 2))
            painter.drawEllipse(QPoint(cx, cy), 5, 5)

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
        self.update_display()

        self.class_selector.clear()
        self.class_selector.addItem("all")
        known_classes = set()
        for kind in ["point", "line"]:
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
