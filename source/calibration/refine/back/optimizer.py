import numpy as np
from scipy.optimize import least_squares

from calibration.base import Calibration
from core.camera import Camera
from core.pointND import PointND
from .error_funk import target_residuals_lsq


class BackProjectionOptimizer(Calibration):
    def __init__(self, camera: Camera, debug_save_path: str = None):
        super().__init__(camera, debug_save_path)

    def run(self, data, **kwargs) -> Camera:
        """
        :param data: данные
        :return: обновлённая камера
        """
        print("[Back] Start refine ...")

        params = self.camera.get_params()
        target_residuals_lsq(self.camera, data, params)
