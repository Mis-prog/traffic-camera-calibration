import numpy as np
from scipy.optimize import least_squares

from camera import Camera
from point import Point


class Optimizer:
    def __init__(self, _camera: Camera):
        self.camera = _camera

    def funk_error(self, line_known, line_predict):
        pointknownStart, pointknownEnd = line_known
        pointpredictStart, pointpredictEnd = line_predict

        error = (
                np.sqrt((pointknownStart.get_image()[0] - pointpredictStart.get_image()[0]) ** 2 +
                        (pointknownStart.get_image()[1] - pointpredictStart.get_image()[1]) ** 2)
                + np.sqrt((pointknownEnd.get_image()[0] - pointpredictEnd.get_image()[0]) ** 2 +
                          (pointknownEnd.get_image()[1] - pointpredictEnd.get_image()[1]) ** 2)
        )
        return error

    def residuals(self, params, lines):
        residuals = []
        for line in lines:
            _point_known_start, _point_known_end = line
            _point_predict_start = self.camera.direct_transform(_point_known_start, params)
            _point_predict_end = self.camera.direct_transform(_point_known_end, params)

            error = self.funk_error(
                [_point_known_start, _point_known_end],
                [_point_predict_start, _point_predict_end]
            )
            residuals.append(error)

        return np.array(residuals)

    def optimize(self, lines):
        angles = self.camera.get_R(angle_output=True)
        x0 = [self.camera.get_f(), angles[0], angles[1], angles[2], 1]
        bounds = (
        (700, 1000),
        (-np.pi, np.pi),
        (-np.pi, np.pi),
        (-np.pi, np.pi),
        (10, 15)
        )
        result = least_squares(self.residuals, x0, args=(lines,), method='lm') 
        return self.camera, result
