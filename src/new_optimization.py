import numpy as np
from scipy.optimize import least_squares
from scipy.optimize import minimize

from .camera_model import Camera
from .pointND import PointND

RESIDUALS = []


class NewOptimization:
    def __init__(self, camera):
        self.camera = camera
        self.params = None

    def set_params(self, params):
        self.params = params

    def _back_project_line_3d(self, start2d, end2d, params):
        pre_start3d = self.camera.back_transform_world(start2d, params)
        pre_end3d = self.camera.back_transform_world(end2d, params)
        return pre_end3d.get() - pre_start3d.get()

    def _angle_restrictions(self, line: np.ndarray, params):
        start2d_1, end2d_1, start2d_2, end2d_2 = line

        line_1 = self._back_project_line_3d(start2d_1, end2d_1, params)
        line_2 = self._back_project_line_3d(start2d_2, end2d_2, params)

        dot_product = np.dot(line_1, line_2)
        norm_known = np.linalg.norm(line_1)
        norm_predicted = np.linalg.norm(line_2)

        cos_theta = np.clip(dot_product / (norm_known * norm_predicted), -1.0, 1.0)
        angle_rad = np.arccos(cos_theta)
        angle_deg = np.degrees(angle_rad)

        return abs(angle_deg - 90)

    def _parallel_restrictions(self, line: np.ndarray, params):
        start2d_1, end2d_1, start2d_2, end2d_2 = line

        line_1 = self._back_project_line_3d(start2d_1, end2d_1, params)
        line_2 = self._back_project_line_3d(start2d_2, end2d_2, params)

        dot_product = np.dot(line_1, line_2)
        norm_known = np.linalg.norm(line_1)
        norm_predicted = np.linalg.norm(line_2)

        cos_theta = np.clip(dot_product / (norm_known * norm_predicted), -1.0, 1.0)

        return abs(1 - cos_theta)

    def _dist_between_line(self, line: np.ndarray, params):
        start2d_1, end2d_1, start2d_2, end2d_2 = line

        line_1 = self._back_project_line_3d(start2d_1, start2d_2, params)
        line_2 = self._back_project_line_3d(end2d_1, end2d_2, params)

        dist_start = np.linalg.norm(line_1)
        dist_end = np.linalg.norm(line_2)

        dist = 19 / 2

        return abs(dist_start - dist) + abs(dist_end - dist)

    def target_function(self, params, data):
        residuals = []

        data_angle = data['angle'] if 'angle' in data and data['angle'].size > 0 else []
        data_parallel_line = data['parallel'] if 'parallel' in data and data['parallel'].size > 0 else []
        data_between_line = data['dist_between_line'] if 'dist_between_line' in data and data[
            'dist_between_line'].size > 0 else []

        for _data in data_angle:
            # print(f'Angle: {self._angle_restrictions(_data, params)}')
            residuals.append(self._angle_restrictions(_data, params))

        for _data in data_parallel_line:
            # print(f'Parallel: {self._parallel_restrictions(_data, params)}')
            residuals.append(self._parallel_restrictions(_data, params))

        for _data in data_between_line:
            residuals.append(self._dist_between_line(_data, params))

        RESIDUALS.append(residuals)
        return residuals

    def back_projection(self, data):
        self.params = [900, -99.58434695, 37.91236625, -167.6947188, 1, 1, 31.72150605]
        bounds = ([500, -180, -180, -180, 5], [2000, 180, 180, 180, 60])
        result = least_squares(self.target_function, self.params, args=(data,), method='lm', verbose=2
                               # , bounds=bounds
                               )
        print(result.cost)
        print(np.around(result.x, 2))
