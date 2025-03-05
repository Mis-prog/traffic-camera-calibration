import cv2
import matplotlib.pyplot as plt
from enum import Enum, auto
from pathlib import Path

import numpy as np

from .camera_model import Camera
from .point2D import Point2D
from .point3D import Point3D


class DisplayMode(Enum):
    INTERACTIVE = auto()
    JUPYTER = auto()
    SAVE = auto()


class Plot:
    def __init__(self, camera):
        self.camera = camera
        self.scene_plot = self.camera.get_scene().copy()

    def _draw_point_with_label(self, img, point, coords):
        cv2.circle(img, point, 5, (0, 0, 255), -1)
        if len(coords) == 2:
            text = f"({coords[0]:.1f}, {coords[1]:.1f})"
        else:
            text = f"({coords[0]:.1f}, {coords[1]:.1f}, {coords[2]:.1f} )"
        cv2.putText(img, text, (point[0] + 5, point[1] - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    def _get_cv2_format(self, point):
        return tuple(map(int, point.get()))

    def _draw_line_with_point(self, line, params=None):
        start, end = line
        params = params or []

        if params:
            start_point = self.camera.direct_transform_world(start, params)
            end_point = self.camera.direct_transform_world(end, params)
        else:
            start_point = start
            end_point = end

        start_plot = self._get_cv2_format(start_point)
        end_plot = self._get_cv2_format(end_point)

        self._draw_point_with_label(self.scene_plot, start_plot, start.get())
        self._draw_point_with_label(self.scene_plot, end_plot, end.get())

        cv2.line(
            self.scene_plot,
            start_plot,
            end_plot,
            (0, 255, 0),
            2
        )


"""
Пример данных 
    [[Point2D, Point3D],
    [Point2D,Point3D]],
    [[],[]],
       
"""


def draw_point(self, points: np.ndarray, params=None):
    pass


def draw_line(self, lines: np.ndarray, params=None):
    params = params or []
    for start, end in lines:
        pass


def visible(self, mode: DisplayMode):
    if mode == DisplayMode.SAVE:
        filename = Path(self.camera.path).name
        cv2.imwrite('calib_' + filename, self.scene_plot)
    elif mode == DisplayMode.JUPYTER:
        scene_rgb = cv2.cvtColor(self.scene_plot, cv2.COLOR_BGR2RGB)
        plt.figure(figsize=(10, 8))
        plt.imshow(scene_rgb)
        plt.axis('off')
        plt.show()
    elif mode == DisplayMode.INTERACTIVE:
        cv2.imshow('Calibration scene', self.scene_plot)  # todo как редактировать размер окна?
        cv2.waitKey(0)
        cv2.destroyAllWindows()
