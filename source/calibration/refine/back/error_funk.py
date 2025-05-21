import numpy as np

from core import Camera, PointND


def target_residuals_lsq(camera: Camera, data: dict, params: list) -> np.ndarray:
    camera.set_params_from_list(params)
    residuals = []
    if "dist_between_line":
        # error = dist_between_line_error()
        pass
    return np.array(residuals)


def sample_3d_line(P0, direction, t0, t1, num_points=10):
    direction = direction / np.linalg.norm(direction)
    ts = np.linspace(t0, t1, num_points)
    return np.array([P0 + t * direction for t in ts])


def dist_between_line_error(camera, line1, line2, dist):
    line1 = [camera.project_back(PointND(point)) for point in line1]
    line2 = [camera.project_back(PointND(point)) for point in line2]
