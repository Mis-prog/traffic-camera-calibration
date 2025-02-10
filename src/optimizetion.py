import numpy as np
from scipy.optimize import least_squares

from .camera_model import Camera
from .point2D import Point2D
from .point3D import Point3D


class Optimizer:
    def __init__(self, camera: Camera):
        self.camera = camera

    def compute_error(self, line_known: tuple[Point2D, Point2D], line_predicted: tuple[Point2D, Point2D]) -> float:
        known_start, known_end = line_known
        predicted_start, predicted_end = line_predicted

        error = np.sqrt(np.sum((known_start.get() - predicted_start.get()) ** 2)) + \
                np.sqrt(np.sum((known_end.get() - predicted_end.get()) ** 2))

        return error

    def residuals(self, params: np.ndarray,
                  lines: list[tuple[tuple[Point2D, Point3D], tuple[Point2D, Point3D]]]) -> np.ndarray:
        residuals = []

        for known_start, known_end in lines:
            known_start_2D, known_start_3D = known_start
            known_end_2D, known_end_3D = known_end

            predicted_start_2D = self.camera.direct_transform(known_start_3D, params)
            predicted_end_2D = self.camera.direct_transform(known_end_3D, params)

            error = self.compute_error((known_start_2D, known_end_2D), (predicted_start_2D, predicted_end_2D))
            residuals.append(error)

        return np.array(residuals)

    def optimize_init(self, lines: list[tuple[tuple[Point2D, Point3D], tuple[Point2D, Point3D]]]):
        angles = self.camera.get_R(angle_output=True)
        x0 = [self.camera.get_f(), *angles, 10]

        bounds = [
            (700, 1000),
            (-np.pi, np.pi),
            (-np.pi, np.pi),
            (-np.pi, np.pi),
            (10, 15)
        ]

        result = least_squares(self.residuals, x0, args=(lines,), method='trf')
        return self.camera, result

    def optimize_model(self, lines: list[tuple[tuple[Point2D, Point3D], tuple[Point2D, Point3D]]]):
        angles = self.camera.get_R(angle_output=True)
        x0 = [self.camera.get_f(), *angles, 10]

        bounds = [
            (700, 1000),
            (-np.pi, np.pi),
            (-np.pi, np.pi),
            (-np.pi, np.pi),
            (10, 15)
        ]

        result = least_squares(self.residuals, x0, args=(lines,), method='trf')
        return self.camera, result
