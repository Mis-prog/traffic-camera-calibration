import numpy as np
from scipy.optimize import least_squares

from calibration.base import Calibration
from core.camera import Camera
from core.pointND import PointND


class BackProjectionOptimizer(Calibration):
    def __init__(self, camera: Camera):
        super().__init__(camera)

    def run(self, data, **kwargs) -> Camera:
        """
        :param data: данные
        :return: обновлённая камера
        """
        print("[Back] Start refine ...")


