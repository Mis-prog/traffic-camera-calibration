import numpy as np
import cv2
from scipy.spatial.transform import Rotation
from .pointND import PointND


class Camera:
    def __init__(self, path_image):
        self.size = list(cv2.imread(path_image).shape[:2])
        self.path = path_image
        self.fx = None
        self.fy = None

        self.K = np.zeros((3, 3))
        self.R = np.zeros((3, 3))
        self.C = np.zeros((3, 1)).reshape(-1, 1)

    def set_params(self, params):
        if len(params) == 5:
            self.calc_K(params[0])
            self.calc_R(params[1:4])
            self.calc_T(z=params[4])
        elif len(params) == 7:
            self.calc_K(params[0])
            self.calc_R(params[1:4])
            self.calc_T(x=params[4], y=params[5], z=params[6])

    def get_f(self):
        return self.fx, self.fy

    def calc_R(self, euler_angles):
        rot = Rotation.from_euler('zxy', euler_angles, degrees=True)
        self.R = rot.as_matrix()

    def get_R(self, angle_output=False, output=False):
        if angle_output:
            angles = Rotation.from_matrix(self.R).as_euler('zxy', degrees=True)
            return angles
        if output:
            print(f'Матрица поворота:\n{self.R}')
        return self.R
    
    def calc_T(self, x=0, y=0, z=0):
        self.C = np.array([x, y, z])

    def get_T(self, output=False):
        if output:
            print(f'Столбец трансляции:\n{self.C}')
        return self.C

    # вычисление внутренней матрицы
    def calc_K(self, f):
        if isinstance(f, (list, tuple)) and len(f) == 2:
            self.fx, self.fy = f
        else:
            self.fx = f
            self.fy = f
        self.K = np.array([[self.fx, 0, self.size[1] / 2],
                           [0, self.fy, self.size[0] / 2],
                           [0, 0, 1]])

    def get_A(self, output=False):
        if output:
            print(f'Внутренние параметры камеры:\n{self.K}')
        return self.K

    def direct(self, point_real: PointND, params=[]) -> PointND:
        if len(params) == 5:
            self.calc_K(params[0])
            self.calc_R(params[1:4])
            self.calc_T(z=params[4])
        elif len(params) == 7:
            self.calc_K(params[0])
            self.calc_R(params[1:4])
            self.calc_T(x=params[4], y=params[5], z=params[6])

        _T = -self.R @ self.C
        _RT = np.hstack([self.R, _T[:, np.newaxis]])
        _AT = self.K @ _RT
        _new_point = PointND(_AT @ point_real.get(out_homogeneous=True), add_weight=False)
        return _new_point
    
    def back(self, point_image:PointND, params=[]) -> PointND:
        pass
    
    def homography(self, point: PointND, params=[], direction='direct') -> PointND:
        """
        Преобразование точки через гомографию между 3D плоскостью (Z=0) и изображением.

        :param point: PointND — входная точка (в изображении или на плоскости)
        :param params: параметры [f, rz, rx, ry, tx, ty, tz] или другие допустимые форматы
        :param direction: 'direct' — из мира в изображение
                        'back' — из изображения в мир
        :return: PointND
        """
        # Установка параметров
        if len(params) == 5:
            self.calc_K(params[0])
            self.calc_R(params[1:4])
            self.calc_T(z=params[4])
        elif len(params) == 6:
            self.calc_K(params[0:2])
            self.calc_R(params[2:5])
            self.calc_T(z=params[5])
        elif len(params) == 7:
            self.calc_K(params[0])
            self.calc_R(params[1:4])
            self.calc_T(x=params[4], y=params[5], z=params[6])

        T = -self.R @ self.C
        RT = np.hstack([self.R, T[:, np.newaxis]])      # [R | t]
        RT = np.delete(RT, 2, axis=1)                   # удаляем третий столбец (оси Z) ⇒ проекция на плоскость Z=0
        H = self.K @ RT                                 # Гомография

        p = point.get(out_homogeneous=True)

        if direction == 'direct':
            transformed = H @ p
        elif direction == 'back':
            H_inv = np.linalg.inv(H)
            transformed = H_inv @ p
        else:
            raise ValueError("Аргумент direction должен быть 'direct' или 'back'.")

        return PointND(transformed, add_weight=False)
