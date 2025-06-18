from abc import ABC, abstractmethod
import numpy as np

from source.core.camera import Camera

RESUALDS = {}
i = 0


class Calibration(ABC):
    def __init__(self, camera: Camera = None, debug_save_path: str = None):
        self.camera = camera

        self.debug_save_path = debug_save_path

    @abstractmethod
    def run(self, data: dict, **kwargs) -> Camera:
        pass

    def compute_total_residuals(self, camera, data, params, residual_blocks):
        global i
        camera.set_params_from_list(params)
        residuals = []

        data_residuals = {}

        for block in residual_blocks:
            res, group = block(camera, data)
            residuals.extend(res)
            data_residuals[group] = res
            # residuals_local.extend([group,res])

        i += 1
        RESUALDS[i] = data_residuals
        return np.array(residuals)

    def compute_total_mse(self, camera, data, params, residual_blocks):
        camera.set_params_from_list(params)

        residuals = 0
        for block in residual_blocks:
            res = block(camera, data)
            residuals += res
        print(residuals)
        return residuals
