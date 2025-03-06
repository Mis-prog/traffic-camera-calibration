import numpy as np
from scipy.optimize import least_squares
from scipy.optimize import minimize

from .camera_model import Camera
from .pointND import PointND


class NewOptimization:
    def __init__(self, camera):
        self.camera = camera
        self.params = None

    def set_params(self, params):
        self.params = params

    def back_projection(self, data):
        def _back_project_line_3d(start2d, end2d):
            pre_start3d = self.camera.back_transform_world(start2d, self.params)
            pre_end3d = self.camera.back_transform_world(end2d, self.params)
            return pre_end3d.get() - pre_start3d.get()

        def _angle_restrictions(line: np.ndarray):
            start2d_1, end2d_1, start2d_2, end2d_2 = line

            line_1 = _back_project_line_3d(start2d_1, end2d_1)
            line_2 = _back_project_line_3d(start2d_2, end2d_2)

            dot_product = np.dot(line_1, line_2)
            norm_known = np.linalg.norm(line_1)
            norm_predicted = np.linalg.norm(line_2)

            cos_theta = np.clip(dot_product / (norm_known * norm_predicted), -1.0, 1.0)
            angle_rad = np.arccos(cos_theta)
            angle_deg = np.degrees(angle_rad)

            return abs(angle_deg - 90)

        def _parallel_restrictions(line: np.ndarray):
            start2d_1, end2d_1, start2d_2, end2d_2 = line

            line_1 = _back_project_line_3d(start2d_1, end2d_1)
            line_2 = _back_project_line_3d(start2d_2, end2d_2)

            dot_product = np.dot(line_1, line_2)
            norm_known = np.linalg.norm(line_1)
            norm_predicted = np.linalg.norm(line_2)

            cos_theta = np.clip(dot_product / (norm_known * norm_predicted), -1.0, 1.0)

            return abs(1 - cos_theta)

        def _dist_between_line(line: np.ndarray, dist):
            start2d_1, end2d_1, start2d_2, end2d_2 = line

            line_1 = _back_project_line_3d(start2d_1, start2d_2)
            line_2 = _back_project_line_3d(end2d_1, end2d_2)

            dist_start = np.linalg.norm(line_1)
            dist_end = np.linalg.norm(line_2)

            return abs(dist_start - dist) + abs(dist_end - dist)

        def target_funk(params):
            residuals = []

            data_angle = data['angle']
            data_dist_between_line = data['dist_between_line']
            data_parallel_line = data['parallel']
            for _data in data_angle:
                residuals.append(_angle_restrictions(_data))

            for _data in data_dist_between_line:
                residuals.append(_dist_between_line(_data, _data[-1]))

            for _data in data_parallel_line:
                residuals.append(_parallel_restrictions(_data))

            return residuals

        x0 = [930, -99.58434695, 37.91236625, -167.6947188, 1, 1, 31.72150605]
        result = least_squares(target_funk, x0, method='lm', verbose=2)