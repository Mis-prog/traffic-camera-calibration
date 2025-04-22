import cv2
import matplotlib.pyplot as plt
from enum import Enum, auto
from pathlib import Path

import numpy as np

from .camera_model import Camera
from .pointND import PointND


class DisplayMode(Enum):
    INTERACTIVE = auto()
    JUPYTER = auto()
    SAVE = auto()


class ProjectionMode(Enum):
    DIRECT = auto()
    BACK = auto()


class Plot:
    def __init__(self, camera: Camera):
        self.camera = camera
        self.scene_plot = self.camera.get_scene().copy()  # копия сцены
        self.overlay = self.scene_plot.copy()  # слой сцены
        self.mode = DisplayMode.INTERACTIVE

    def set_mode(self, mode: DisplayMode):
        self.mode = mode

    def _transform_pointND_to_cv2_format(self, point: PointND):
        if point:
            return tuple(map(int, point.get()))

    def _draw_point_with_label(self, point2d, coords):
        cv2.circle(self.overlay, point2d, 5, (0, 0, 255), -1)
        if len(coords) == 2:
            text = f"({coords[0]:.1f}, {coords[1]:.1f})"
        else:
            text = f"({coords[0]:.1f}, {coords[1]:.1f}, {coords[2]:.1f} )"
        cv2.putText(self.overlay, text, (point2d[0] + 5, point2d[1] - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    def draw_point(self, points: np.ndarray, params=None, mode=ProjectionMode.DIRECT):
        if self.mode == DisplayMode.JUPYTER:
            self.overlay = self.scene_plot.copy()

        params = params or []
        for point in points:
            point_plot = None

            if params:
                if ProjectionMode.DIRECT:
                    point_plot = self.camera.direct_full(point, params)
                elif ProjectionMode.BACK:
                    point_plot = self.camera.back_crop(point, params)
            else:
                point_plot = point

            point_plot = self._transform_pointND_to_cv2_format(point_plot)
            self._draw_point_with_label(point_plot, point.get())

        alpha = 0.8
        cv2.addWeighted(self.overlay, alpha, self.scene_plot, 1 - alpha, 0, self.scene_plot)

    def draw_line(self, lines: np.ndarray, params=None, mode=ProjectionMode.DIRECT, color=(255, 0, 0), thickness=2):
        if self.mode == DisplayMode.JUPYTER:
            self.overlay = self.scene_plot.copy()

        params = params or []
        for line in lines:
            start, end = line
            start_plot, end_plot = None, None

            if params:
                if mode == ProjectionMode.DIRECT:
                    start_plot = self.camera.direct_full(start, params)
                    end_plot = self.camera.direct_full(end, params)
                elif mode == ProjectionMode.BACK:
                    start_plot = self.camera.back_crop(start, params)
                    end_plot = self.camera.back_crop(end, params)
            else:
                start_plot = start
                end_plot = end

            start_plot = self._transform_pointND_to_cv2_format(start_plot)
            end_plot = self._transform_pointND_to_cv2_format(end_plot)
            self._draw_point_with_label(start_plot, start.get())
            self._draw_point_with_label(end_plot, end.get())

            cv2.line(
                self.overlay,
                start_plot,
                end_plot,
                color,
                thickness
            )

        alpha = 0.8
        cv2.addWeighted(self.overlay, alpha, self.scene_plot, 1 - alpha, 0, self.scene_plot)

    def visible(self, mode: DisplayMode = None):
        mode = mode or self.mode

        if mode == DisplayMode.SAVE:
            filename = Path(self.camera.path).name
            print('calib_' + filename)
            cv2.imwrite('calibline_' + filename, self.overlay)
        elif mode == DisplayMode.JUPYTER:
            scene_rgb = cv2.cvtColor(self.overlay, cv2.COLOR_BGR2RGB)
            plt.figure(figsize=(10, 8))
            # plt.title()
            plt.imshow(scene_rgb)
            plt.axis('off')
            plt.show()
        elif mode == DisplayMode.INTERACTIVE:
            cv2.namedWindow('Calibration scene', cv2.WINDOW_NORMAL)
            initial_width = 1000  # Ширина окна
            initial_height = 700  # Высота окна
            cv2.resizeWindow('Calibration scene', initial_width, initial_height)
            cv2.imshow('Calibration scene', self.overlay)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
