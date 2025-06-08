import numpy as np

from core import Camera, PointND
from calibration.utils import gps_to_enu


def residual_reprojection_line(camera, data, group, gps_origin):
    residuals = []
    lines = data.get(group, [])
    for line in lines:
        p1, p2 = line['pixel']
        P1, P2 = line['gps']
        _p1 = camera.project_direct(PointND([*gps_to_enu(*P1, *gps_origin), 0])).get()
        _p2 = camera.project_direct(PointND([*gps_to_enu(*P2, *gps_origin), 0])).get()
        error1 = np.sum((np.array(_p2) - np.array(p2)) ** 2)
        error2 = np.sum((np.array(_p1) - np.array(p1)) ** 2)
        error = np.sqrt(error1 + error2)
        residuals.append(error)
    return residuals


def line_projection_error(camera: Camera, line, gps_origin):
    p1, p2 = line['pixel']
    P1, P2 = line['gps']
    P1, P2 = gps_to_enu(*gps_origin, *P1)

    return 0


def point_projection_error(camera: Camera, point) -> float:
    point2D, point3D = point
    proj2D = camera.project_direct(point3D)
    return np.linalg.norm(point2D.get() - proj2D.get())
