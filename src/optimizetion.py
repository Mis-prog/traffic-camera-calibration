import numpy as np
from scipy.optimize import least_squares

from .camera_model import Camera
from .point2D import Point2D
from .point3D import Point3D


class Optimizer:
    def __init__(self, camera: Camera):
        self.camera = camera

    def error_point_to_point(self, line_known: tuple[Point2D, Point2D],
                             line_predicted: tuple[Point2D, Point2D]) -> float:
        known_start, known_end = line_known
        predicted_start, predicted_end = line_predicted

        error = np.sqrt(np.sum((known_start.get() - predicted_start.get()) ** 2)) + \
                np.sqrt(np.sum((known_end.get() - predicted_end.get()) ** 2))

        return error

    def error_line(self, line_known: tuple[Point2D, Point2D], line_predicted: tuple[Point2D, Point2D]) -> float:
        known_start, known_end = line_known
        predicted_start, predicted_end = line_predicted

        x1, x2 = known_start.get()[0], known_end.get()[0]
        y1, y2 = known_start.get()[1], known_end.get()[1]

        predicted_points = np.array([
            [predicted_start.get()[0], predicted_start.get()[1]],
            [predicted_end.get()[0], predicted_end.get()[1]]
        ])

        x, y = predicted_points[:, 0], predicted_points[:, 1]
        error = np.abs((x - x1) / (x2 - x1) - (y - y1) / (y2 - y1))

        return np.sum(error)

    def reprojection_error(self, line_known: tuple[Point2D, Point2D],
                           line_predicted: tuple[Point2D, Point2D]) -> float:
        known_start, known_end = map(lambda p: np.array(p.get()), line_known)
        predicted_points = np.array([line_predicted[0].get(), line_predicted[1].get()])

        # Найдем коэффициенты прямой Ax + By + C = 0 для known
        x1, y1 = known_start
        x2, y2 = known_end
        A, B = y2 - y1, x1 - x2  # Нормаль (перпендикулярный вектор)
        C = -A * x1 - B * y1

        # Вычислим расстояние от точек предсказанной линии до прямой
        distances = np.abs(A * predicted_points[:, 0] + B * predicted_points[:, 1] + C) / np.sqrt(A ** 2 + B ** 2)

        return np.mean(distances)  # Средняя ошибка перепроецирования

    def residuals(self, params: np.ndarray,
                  lines: list[tuple[tuple[Point2D, Point3D], tuple[Point2D, Point3D]]]) -> np.ndarray:
        residuals = []

        for known_start, known_end in lines:
            known_start_2D, known_start_3D = known_start
            known_end_2D, known_end_3D = known_end

            predicted_start_2D = self.camera.direct_transform_world(known_start_3D, params)
            predicted_end_2D = self.camera.direct_transform_world(known_end_3D, params)

            error1 = self.error_point_to_point((known_start_2D, known_end_2D), (predicted_start_2D, predicted_end_2D))
            error2 = self.reprojection_error((known_start_2D, known_end_2D), (predicted_start_2D, predicted_end_2D))
            residuals.append(error1+error2)

        return np.array(residuals)

    def optimize(self, lines: list[tuple[tuple[Point2D, Point3D], tuple[Point2D, Point3D]]]):
        angles = self.camera.get_R(angle_output=True)
        # x0 = [self.camera.get_f(), *angles, 10]
        x0 = [931.45763154, -99.58434695, 37.91236625, -167.6947188, 31.72150605]

        bounds = [
            (700, 1000),
            (-np.pi, np.pi),
            (-np.pi, np.pi),
            (-np.pi, np.pi),
            (10, 15)
        ]

        result = least_squares(self.residuals, x0, args=(lines,), method='trf')
        return self.camera, result
