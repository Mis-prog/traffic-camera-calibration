import numpy as np

from core import Camera, PointND


def residual_reprojection_line(camera, data, group):
    residuals = []
    lines = data.get(group, [])
    for line in lines:
        pass


def point_projection_error(camera: Camera, point) -> float:
    point2D, point3D = point
    proj2D = camera.project_direct(point3D)
    return np.linalg.norm(point2D.get() - proj2D.get())
