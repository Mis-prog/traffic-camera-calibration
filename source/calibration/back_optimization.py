import numpy as np
from scipy.optimize import least_squares
from scipy.optimize import minimize

from source.camera_model import Camera
from source.pointND import PointND
from source.data_preparation import fun_lines

RESIDUALS = []
PARAMS = []


class BackProjectionOptimizer:
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

        # return abs(angle_deg - 90) ** 2
        loss = np.exp(abs(angle_deg - 90) / 10) - 1
        loss = abs(angle_deg - 90)

        return abs(dot_product) ** 2 * 50

    def _parallel_restrictions(self, line: np.ndarray, params):
        start2d_1, end2d_1, start2d_2, end2d_2 = line

        line_1 = self._back_project_line_3d(start2d_1, end2d_1, params)
        line_2 = self._back_project_line_3d(start2d_2, end2d_2, params)

        dot_product = np.dot(line_1, line_2)
        norm_known = np.linalg.norm(line_1)
        norm_predicted = np.linalg.norm(line_2)

        cos_theta = np.clip(dot_product / (norm_known * norm_predicted), -1.0, 1.0)

        return (1 - cos_theta ** 2)

    def _point_to_point(self, line: np.ndarray, params, log_calc=False):
        start, end = line

        line = self._back_project_line_3d(start, end, params)

        dist_calc = np.linalg.norm(line)

        dist = 40  # в дм

        # if 40 <= dist_calc <= 60:
        #     return np.log(abs(dist_calc - dist))
        # else:
        #     return abs(dist_calc - dist) ** 2
        # return  50 * np.log1p(abs(dist_calc-dist))

        return np.log1p(abs(dist_calc - dist)) ** 2

    def _dist_between_line(self, line: np.ndarray, y_dist, params):
        start2d_1, end2d_1, start2d_2, end2d_2 = line

        # Векторы прямых
        line_1 = self._back_project_line_3d(start2d_1, end2d_1, params)
        line_2 = self._back_project_line_3d(start2d_2, end2d_2, params)

        cross = np.cross(line_1, line_2)
        cross_norm = np.linalg.norm(cross)

        if cross_norm < 1e-6:
            # Прямые параллельны — расстояние от точки до прямой
            return np.linalg.norm(np.cross((start2 - start1), u)) / np.linalg.norm(u)

        # Иначе — расстояние между скрещивающимися прямыми
        distance = abs(np.dot(w, cross)) / cross_norm
        return distance

    def target_function(self, params, data):

        residuals = []

        data_angle = data['angle'] if 'angle' in data and data['angle'].size > 0 else []
        data_parallel_line_1 = data['parallel-1'] if 'parallel-1' in data and data['parallel-1'].size > 0 else []
        data_point_to_point = data['point_to_point'] if 'point_to_point' in data and data[
            'point_to_point'].size > 0 else []
        data_parallel_line_2 = data['parallel-2'] if 'parallel-2' in data and data['parallel-2'].size > 0 else []
        data_parallel_line_3 = data['parallel-3'] if 'parallel-3' in data and data['parallel-3'].size > 0 else []
        data_parallel_line_4 = data['parallel-4'] if 'parallel-4' in data and data['parallel-4'].size > 0 else []
        data_parallel_line_5 = data['parallel-5'] if 'parallel-5' in data and data['parallel-5'].size > 0 else []
        data_point_to_point_2 = data['point_to_point_2'] if 'point_to_point_2' in data and data[
            'point_to_point_2'].size > 0 else []
        for _data in data_angle:
            #     # print(f'Angle: {self._angle_restrictions(_data, params)}')
            residuals.append(self._angle_restrictions(_data, params))

        for dist, _data in zip([-11, 11], data_parallel_line_1):
            residuals.append(self._parallel_restrictions(_data, params))
            # residuals.append(self._dist_between_line(_data, dist, params))

        for dist, _data in zip([-7, 7], data_parallel_line_2):
            residuals.append(self._parallel_restrictions(_data, params))
            # residuals.append(self._dist_between_line(_data, dist, params))

        for dist, _data in zip([-7, 7], data_parallel_line_3):
            residuals.append(self._parallel_restrictions(_data, params))
            # residuals.append(self._dist_between_line(_data, dist, params))

        for dist, _data in zip([-7, 7], data_parallel_line_4):
            residuals.append(self._parallel_restrictions(_data, params))
            # residuals.append(self._dist_between_line(_data, dist, params))

        for dist, _data in zip([-7, 7], data_parallel_line_5):
            residuals.append(self._parallel_restrictions(_data, params))
            # residuals.append(self._dist_between_line(_data, dist, params))

        for _data in data_point_to_point:
            residuals.append(self._point_to_point(_data, params))

        for _data in data_point_to_point_2:
            residuals.append(self._point_to_point(_data, params))

        RESIDUALS.append(np.array(residuals))
        PARAMS.append(params)

        return np.concatenate([np.ravel(res) for res in residuals])
        # return np.sum(residuals)

    def normalize_angle_deg(self, angle):
        return (angle + 180) % 360 - 180

    def back_projection(self, data):
        self.params = [3000, - 180, 0.91236625, -180.6947188, 150]

        bounds = ([900, -360, -360, -360, 100], [10000, 360, 360, 360, 600])
        # self.params = np.random.uniform(low=bounds[0], high=bounds[1])
        result = least_squares(self.target_function, self.params, args=(data,), method='trf',
                               verbose=2,
                               bounds=bounds,
                               loss='soft_l1',
                               jac='3-point'
                               # ftol=1e-8,   xtol=1e-8, gtol=1e-8
                               )
        # result = minimize(self.target_function, self.params, args=(data,), method='Nelder-Mead',
        #                   bounds=list(zip(bounds[0], bounds[1])),options={'maxiter': 3000, 'disp': True})
        result_to_numpy = np.array(result.x)
        np.savetxt('../../example/pushkin_aksakov/marked_data_new/calib_data.txt',
                   [np.around(result_to_numpy, 2)], fmt='%.2f', delimiter=' ', newline='')
        print(f'f: {result.x[0]}')
        print(
            f'Z: {self.normalize_angle_deg(result.x[1])}, X: {self.normalize_angle_deg(result.x[2])}, Y: {self.normalize_angle_deg(result.x[3])}')
        print(f'H: {result.x[4]}')

    def print_result(self):
        pass
