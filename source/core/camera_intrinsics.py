import numpy as np


class CameraIntrinsics:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.fx = None
        self.fy = None
        self.K = np.eye(3)

    def set_focal_length(self, f):
        self.fx, self.fy = (f, f) if not isinstance(f, (tuple, list)) else f
        self.K = np.array([[self.fx, 0, self.width / 2],
                           [0, self.fy, self.height / 2],
                           [0, 0, 1]])

    def get(self):
        return self.K

    def get_main_point(self):
        return self.width / 2, self.height / 2

    def get_focal_length(self):
        if self.fx == self.fy:
            return self.fx
        else:
            return (self.fx, self.fy)
