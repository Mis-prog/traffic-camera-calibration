import numpy as np
from scipy.optimize import least_squares

from calibration.base import Calibration
from core.camera import Camera
from core.pointND import PointND


class DirectProjectionOptimizer(Calibration):
    def __init__(self, camera: Camera):
        super().__init__(camera)

    def run(self, data, **kwargs) -> Camera:
        """
        :param data
        :return: обновлённая камера
        """
        print("[Direct] Start refine ...")

        x0 = kwargs.get("x0", self.camera.get_params())
        solver = kwargs.get("solver", least_squares)

        return self.camera
