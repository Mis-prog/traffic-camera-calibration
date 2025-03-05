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
        def angle_restrictions(line: np.ndarray):
            start2d_1, end2d_1, start2d_2, end2d_2 = line

            pre_start3d_1 = self.camera.back_transform_world(start2d_1, self.params)
            pre_end3d_1 = self.camera.back_transform_world(end2d_1, self.params)
            pre_start3d_2 = self.camera.back_transform_world(start2d_2, self.params)
            pre_end3d_2 = self.camera.back_transform_world(end2d_2, self.params)

            line_1 = pre_end3d_1.get() - pre_start3d_1.get()
            line_2 = pre_end3d_2.get() - pre_start3d_2.get()

            dot_product = np.dot(line_1, line_2)
            norm_known = np.linalg.norm(line_1)
            norm_predicted = np.linalg.norm(line_2)

            cos_theta = np.clip(dot_product / (norm_known * norm_predicted), -1.0, 1.0)
            angle_rad = np.arccos(cos_theta)
            angle_deg = np.degrees(angle_rad)

            return abs(angle_deg - 90)

        def parallelism_restrictions(line: np.ndarray):
            start2d_1, end2d_1, start2d_2, end2d_2 = line
            pre_start3d_1 = self.camera.back_transform_world(start2d_1, self.params)
            pre_end3d_1 = self.camera.back_transform_world(end2d_1, self.params)
            pre_start3d_2 = self.camera.back_transform_world(start2d_2, self.params)
            pre_end3d_2 = self.camera.back_transform_world(end2d_2, self.params)

            line_1 = pre_end3d_1.get() - pre_start3d_1.get()
            line_2 = pre_end3d_2.get() - pre_start3d_2.get()

            dot_product = np.dot(line_1, line_2)
            norm_known = np.linalg.norm(line_1)
            norm_predicted = np.linalg.norm(line_2)

            cos_theta = np.clip(dot_product / (norm_known * norm_predicted), -1.0, 1.0)

            return abs(1 - cos_theta)

        def dist_between_line(line: np.ndarray):
            start2d_1, end2d_1, start2d_2, end2d_2 = line
            pre_start3d_1 = self.camera.back_transform_world(start2d_1, self.params)
            pre_end3d_1 = self.camera.back_transform_world(end2d_1, self.params)
            pre_start3d_2 = self.camera.back_transform_world(start2d_2, self.params)
            pre_end3d_2 = self.camera.back_transform_world(end2d_2, self.params)



        data_angle = data['angle']
        data_dist_between_line = data['line']
