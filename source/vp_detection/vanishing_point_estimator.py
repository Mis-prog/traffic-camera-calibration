import numpy as np

from .base import Detector


class VanishingPointEstimatorManual(Detector):
    def __init__(self):
        pass

    @staticmethod
    def _normal_vector(x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        normal = np.array([-dy, dx]) / np.hypot(dx, dy)
        return normal

    def estimate(self, lines):
        A = []
        b = []
        for (x1, y1), (x2, y2) in lines:
            n = self._normal_vector(x1, y1, x2, y2)
            A.append(n)
            b.append(np.dot(n, [x1, y1]))
        A = np.array(A)
        b = np.array(b)
        vp = np.linalg.lstsq(A, b, rcond=None)[0]
        return vp
