import numpy as np
from scipy.optimize import least_squares

from calibration.base import Calibration
from core.camera import Camera
from core.pointND import PointND
from .error_funk import target_residuals_lsq


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
        method = kwargs.get("method", "lm")

        def residuals(params):
            return target_residuals_lsq(self.camera, data, params)

        result = solver(residuals, x0,
                        method=method,
                        verbose=2,
                        max_nfev=10000)
        self.camera.set_params_from_list(result.x)

        return self.camera
