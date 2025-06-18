import numpy as np

from core.camera import Camera


def get_plane_normal(camera, p1, p2):
    r1 = camera.backproject_ray(p1)  # (3,)
    r2 = camera.backproject_ray(p2)  # (3,)
    normal = np.cross(r1, r2)
    return normal / np.linalg.norm(normal)
