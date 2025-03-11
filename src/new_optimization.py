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

        return 2 * abs(1 - cos_theta)

    def _point_to_point(self, line: np.ndarray, params, log_calc=False):
        start, end = line

        line = self._back_project_line_3d(start, end, params)

        dist_calc = np.linalg.norm(line)

        dist = 4.2

        if not log_calc:
            return abs(dist_calc - dist)
        else:
            return np.log(abs(dist_calc - dist))

    def _dist_between_line(self, line: np.ndarray, params, log_calc=False):
        start2d_1, end2d_1, start2d_2, end2d_2 = line
        line_1 = self._back_project_line_3d(start2d_1, start2d_2, params)
        line_2 = self._back_project_line_3d(end2d_1, end2d_2, params)

        dist_start = np.linalg.norm(line_1)
        dist_end = np.linalg.norm(line_2)
        print(dist_start, dist_end)
        dist = 20 / 2

        if not log_calc:
            # return (dist_start + dist_end) / 2 - dist
            return abs(dist_start - dist_end)
        else:
            return np.log(abs(dist_start - dist)) + np.log1p(abs(dist_end - dist))

    def target_function(self, params, data):
        residuals = []

        data_angle = data['angle'] if 'angle' in data and data['angle'].size > 0 else []
        data_parallel_line = data['parallel'] if 'parallel' in data and data['parallel'].size > 0 else []
        data_point_to_point = data['point_to_point'] if 'point_to_point' in data and data[
            'point_to_point'].size > 0 else []
        data_parallel_line_2 = data['parallel_2'] if 'parallel_2' in data and data['parallel_2'].size > 0 else []

        for _data in data_angle:
            #     # print(f'Angle: {self._angle_restrictions(_data, params)}')
            residuals.append(self._angle_restrictions(_data, params))

        for _data in data_parallel_line:
            residuals.append(self._parallel_restrictions(_data, params))
            # residuals.append(self._dist_between_line(_data, params))
        for _data in data_parallel_line_2:
            # print(self._parallel_restrictions(_data, params))
            residuals.append(self._parallel_restrictions(_data, params))

        for _data in data_point_to_point:
            residuals.append(self._point_to_point(_data, params))

        RESIDUALS.append(np.array(residuals))
        PARAMS.append(params)
        return residuals
        # return np.sum(np.array(residuals) ** 2)

    def back_projection(self, data):
        self.params = [1200, -99.58434695, 37.91236625, -167.6947188, 10]

        bounds = ([700, -180, -180, -180, 5], [2000, 180, 180, 180, 60])
        # self.params = np.random.uniform(low=bounds[0], high=bounds[1])
        result = least_squares(self.target_function, self.params, args=(data,), method='trf',
                               verbose=2,
                               bounds=bounds,
                               # loss='huber',
                               # jac='3-point'
                               # ftol=1e-8, xtol=1e-8, gtol=1e-8
                               )
        # result = minimize(self.target_function, self.params, args=(data,), method='Nelder-Mead',
        #                   bounds=list(zip(bounds[0], bounds[1])),options={'maxiter': 1000, 'disp': True})
        print(*np.around(result.x, 2))
