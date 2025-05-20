import numpy as np

from core import Camera, PointND


def target_residuals_lsq(camera: Camera, data: dict, params: list) -> np.ndarray:
    camera.set_params_from_list(params)
    residuals = []
    if "dist_between_line":
        pass

    return np.array(residuals)


def dist_between_line_error(line):
    pass