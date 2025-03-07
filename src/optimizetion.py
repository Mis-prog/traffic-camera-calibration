import numpy as np
from scipy.optimize import least_squares
from scipy.optimize import minimize

from .camera_model import Camera
from .point2D import Point2D
from .point3D import Point3D
from .pointND import PointND


class Optimizer:
    def __init__(self, camera: Camera):
        self.camera = camera

    def error_point_to_point(self, line_known: tuple[Point2D, Point2D],
                             line_predicted: tuple[Point2D, Point2D]) -> float:
        known_start, known_end = line_known
        predicted_start, predicted_end = line_predicted

        error = np.linalg.norm(known_start.get() - predicted_start.get()) + \
                np.linalg.norm(known_end.get() - predicted_end.get())

        return error

    def error_line(self, line_known: tuple[Point2D, Point2D],
                   line_predicted: tuple[Point2D, Point2D]) -> float:
        known_start, known_end = line_known
        predicted_start, predicted_end = line_predicted

        # Длина линий
        known_length = np.linalg.norm(known_end.get() - known_start.get())
        predicted_length = np.linalg.norm(predicted_end.get() - predicted_start.get())

        def compute_angle(p1, p2):
            delta = p2.get() - p1.get()
            return np.arctan2(delta[1], delta[0])

        known_angle = compute_angle(known_start, known_end)
        predicted_angle = compute_angle(predicted_start, predicted_end)

        # Ошибка по длине
        length_error = abs(predicted_length - known_length)

        # Ошибка по углу (в радианах)
        angle_error = abs(predicted_angle - known_angle)

        # return length_error + 10 * angle_error
        # print(angle_error)
        return 10 * angle_error

    def residuals_reprojection(self, params: np.ndarray,
                               lines: list[tuple[tuple[Point2D, Point3D], tuple[Point2D, Point3D]]]) -> np.ndarray:
        residuals = []

        for known_start, known_end in lines:
            known_start_2D, known_start_3D = known_start
            known_end_2D, known_end_3D = known_end

            predicted_start_2D = self.camera.direct_full(known_start_3D, params)
            predicted_end_2D = self.camera.direct_full(known_end_3D, params)

            error1 = self.error_point_to_point((known_start_2D, known_end_2D), (predicted_start_2D, predicted_end_2D))
            error2 = self.error_line((known_start_2D, known_end_2D), (predicted_start_2D, predicted_end_2D))
            error3 = self.error_shape((known_start_2D, known_end_2D), (predicted_start_2D, predicted_end_2D))
            # residuals.append(log_error(error1) +   log_error(error2))
            # residuals.append(error1 + error2)
            residuals.append(0.2 * error1 + error2)
        return np.array(residuals)

    def optimize_reprojection(self, lines: list[tuple[tuple[Point2D, Point3D], tuple[Point2D, Point3D]]]):
        angles = self.camera.get_R(angle_output=True)
        # x0 = [self.camera.get_f() , *angles, 20]
        # x0 = [900, -99.58434695, 37.91236625, -167.6947188, 31.72150605]
        x0 = [930, -99.58434695, 37.91236625, -167.6947188, 1, 1, 31.72150605]

        cost_history = []
        history = []

        def wrapped_residuals(params):
            residuals = self.residuals_reprojection(params, lines)
            cost = 0.5 * np.sum(residuals ** 2)  # Вычисляем cost
            cost_history.append(cost)  # Сохраняем cost
            history.append(params.copy())
            return residuals

        # bounds = ([800, -180, -180, -180, 10], [1500, 180, 180, 180, 60])
        result = least_squares(wrapped_residuals, x0, method='lm', verbose=2, max_nfev=10000)

        return self.camera, result, cost_history, history

    def optimize_back_reprojection_LM(self, lines: list[tuple[tuple[Point2D, Point2D], tuple[Point2D, Point2D]]]):
        angles = self.camera.get_R(angle_output=True)
        # x0 = [self.camera.get_f(), *angles, 10]
        x0 = [931.45763154, -99.58434695, 37.91236625, -167.6947188, 31.72150605]
        #
        result = least_squares(self.residuals_back_reprojection, x0, args=(lines,), method='lm',
                               verbose=2,  # подробно видно как сходится
                               loss='huber',
                               # max_nfev=20000 # кол-во итераций
                               )
        return self.camera, result

    def optimize_back_reprojection_NM(self, lines: list[tuple[tuple[Point2D, Point2D], tuple[Point2D, Point2D]]]):
        angles = self.camera.get_R(angle_output=True)
        # x0 = [self.camera.get_f(), *angles, 10]
        x0 = [931.45763154, -50, 0, -150, 31.72150605]

        def callback(xk):
            residuals = self.residuals_back_reprojection(xk, lines)
            loss = sum(residuals ** 2)
            print(f"Function value at iteration: {loss}")

        result = minimize(
            lambda x: sum(self.residuals_back_reprojection(x, lines) ** 2),  # Сумма квадратов ошибок
            x0,
            method='Nelder-Mead',
            options={
                'maxiter': 1000,
                'disp': True  # Показывать процесс оптимизации
            },
            callback=callback
        )

        return self.camera, result

    def residuals_back_reprojection(self, params: np.ndarray, primitive) -> np.ndarray:
        def error_between_line(params, primitive):
            pass

        def error_between_angle(params, lines: tuple[Point2D, Point2D, Point2D, Point2D]):
            start1, end1, start2, end2 = lines

            start1_3D = self.camera.back_crop(start1, params)
            end1_3D = self.camera.back_crop(end1, params)
            start2_3D = self.camera.back_crop(start2, params)
            end2_3D = self.camera.back_crop(end2, params)

        residuals = []

        return np.array(residuals)