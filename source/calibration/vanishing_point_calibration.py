import numpy as np

from base import Calibration
from core import Camera


class VanishingPointCalibration(Calibration):
    def __init__(self, camera: Camera):
        super().__init__(camera)
        self.vp1 = None  # vanishing point 1
        self.vp2 = None  # vanishing point 2
        self.vp3 = None  # vanishing point 3

    def set_vanishing_points(self, vp1, vp2, vp3):
        self.vp1 = np.array(vp1, dtype=float)
        self.vp2 = np.array(vp2, dtype=float)
        self.vp3 = np.array(vp3, dtype=float)

    def calc_f(self, cx, cy):
        if self.vp1 is None or self.vp2 is None:
            raise ValueError("vp1 and vp2 must be set")

        v1 = np.append(self.vp1, 1.0)  # make homogeneous
        v2 = np.append(self.vp2, 1.0)
        c = np.array([cx, cy, 1.0])

        term = np.dot(v1 - c, c - v2)

        if term <= 0:
            raise ValueError("Invalid configuration: value under sqrt is non-positive")

        f = np.sqrt(term)
        return f

    def calc_R(self, f):
        self.camera.calc_K(f)
        K_inv = np.linalg.inv(self.camera.get_K())

        d1 = K_inv @ np.append(self.vp1, 1.0)  # направление X_w
        d2 = K_inv @ np.append(self.vp2, 1.0)  # направление Y_w
        d3 = K_inv @ np.append(self.vp3, 1.0)  # направление Z_w

        d1 /= np.linalg.norm(d1)
        d2 /= np.linalg.norm(d2)
        d3 /= np.linalg.norm(d3)

        R = np.stack([d1, d2, d3], axis=1)  # колонки — оси в мировых координатах

        self.camera.extrinsics.R = R
        return R
