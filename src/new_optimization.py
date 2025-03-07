import numpy as np
from scipy.optimize import least_squares
from scipy.optimize import minimize

from .camera_model import Camera
from .pointND import PointND

RESIDUALS = []
PARAMS = []


class NewOptimization:
    def __init__(self, camera):
        self.camera = camera
        self.params = None

    def set_params(self, params):
        self.params = params

    def _back_project_line_3d(self, start2d: PointND, end2d: PointND, params):
        # print(start2d.get(out_homogeneous=True))
        pre_start3d = self.camera.back_crop(start2d, params)
        pre_end3d = self.camera.back_crop(end2d, params)
        # print(pre_start3d.get())
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

    def _point_to_point(self, line: np.ndarray, params):
        start, end = line

        line = self._back_project_line_3d(start, end, params)

        dist_calc = np.linalg.norm(line)

        dist = 4

        return abs(dist_calc - dist)

    def target_function(self, params, data):
        residuals = []

        data_angle = data['angle'] if 'angle' in data and data['angle'].size > 0 else []
        data_parallel_line = data['parallel'] if 'parallel' in data and data['parallel'].size > 0 else []
        data_between_line = data['point_to_point'] if 'point_to_point' in data and data[
            'point_to_point'].size > 0 else []

        for _data in data_angle:
            # print(f'Angle: {self._angle_restrictions(_data, params)}')
            residuals.append(self._angle_restrictions(_data, params))

        for _data in data_parallel_line:
            # print(f'Parallel: {self._parallel_restrictions(_data, params)}')
            residuals.append(self._parallel_restrictions(_data, params))

        for _data in data_between_line:
            residuals.append(self._point_to_point(_data, params))

        RESIDUALS.append(residuals)
        PARAMS.append(params)
        return residuals

    def back_projection(self, data):
        self.params = [1200, -99.58434695, 37.91236625, -167.6947188, 31.72150605]
        bounds = ([500, -360, -360, -360, 5], [2000, 360, 360, 360, 60])
        # self.params = np.log1p(self.params)
        # print(self.params)

        result = least_squares(self.target_function, self.params, args=(data,), method='trf', verbose=2,
                                bounds=bounds
                               )
        print(*np.around(result.x, 2))
        # print("Градиенты (Якобиан):", result.jac)
