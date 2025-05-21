import numpy as np

from core import Camera, PointND


def target_residuals_lsq(camera: Camera, data: dict, params:list) -> np.ndarray:
    camera.set_params_from_list(params)
    residuals = []
    if "point" in data:
        for pair in data["point"]:
            err = point_projection_error(camera, pair)
            residuals.append(err)

    return np.array(residuals)


def target_residuals_cost(camera: Camera, data: dict, params) -> float:
    camera.set_params(params)
    residuals = []
    if "point" in data:
        for pair in data["point"]:
            err = point_projection_error(camera, pair)
            residuals.append(err)

    return np.sum(np.array(residuals))


def point_projection_error(camera: Camera, point) -> float:
    point2D, point3D = point
    proj2D = camera.project_direct(point3D)
    return np.linalg.norm(point2D.get() - proj2D.get())
