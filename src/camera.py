import numpy as np
import cv2
from scipy.spatial.transform import Rotation
from point import Point


class Camera:
    def __init__(self):
        self.size = None
        self.scene = None
        self.tau = None
        self.f = None

        self.A = np.zeros((3, 3))
        self.R = np.zeros((3, 3))
        self.T = np.zeros((3, 1)).reshape(-1, 1)

    def get_scene(self):
        return self.scene

    def get_f(self):
        return self.f

    def get_tau(self):
        return self.tau

    def load_scene(self, path):
        self.scene = cv2.imread(path)
        height, width, channels = self.scene.shape
        self.size = [height, width]  # высота и ширина
        self.tau = height / width

    # вычисление матрицы поворота
    def calc_R(self, euler_angles):
        rot = Rotation.from_euler('zxy', euler_angles, degrees=True)
        self.R = rot.as_matrix()

    def set_init_R(self, p):
        self.R = np.vstack(p).transpose()

    def get_R(self, angle_output=False, output=False):
        if angle_output:
            angles = Rotation.from_matrix(self.R).as_euler('zxy', degrees=True)
            # print(f'Углы Эйлера:\n{angles}')
            return angles
        if output:
            print(f'Матрица поворота:\n{self.R}')
        return self.R

    # вычисление столбца переноса
    def calc_T(self, x=0, y=0, z=0):
        self.T = np.array([x, y, z])

    def get_T(self, output=False):
        if output:
            print(f'Столбец переноса:\n{self.T}')
        return self.T

    # вычисление внутренней матрицы
    def calc_A(self, f, using_tau=True):
        self.f = f
        if using_tau:
            self.A = np.array([[f, 0, self.size[1]/2],
                               [0, f * self.tau, self.size[0]/2],
                               [0, 0, 1]])
        else:
            self.A = np.array([[f, 0, self.size[1]/2],
                               [0, f, self.size[0]/2],
                               [0, 0, 1]])

    def get_A(self, output=False):
        if output:
            print(f'Внутренние параметры камеры:\n{self.A}')
        return self.A

    # прямое преобразование
    def direct_transform(self, point_real: Point, params=[]) -> Point:
        if len(params) > 5:
            self.calc_A(params[0])
            self.calc_R(params[1:4])
            self.calc_T(x=params[4], y=params[5], z=params[6])
        _T1 = -self.R @ self.T
        _RT = np.hstack([self.R,_T1[:, np.newaxis]])
        _AT = self.A @ _RT
        _new_point = _AT @ point_real.get_real_full()
        point_image = Point.copy(point_real)
        point_image.set_image(_new_point)
        return point_image

    # обратное преобразование
    def back_transform(self, point_image: Point, params=[]) -> Point:
        if len(params) > 5:
            self.calc_A(params[0])
            self.calc_R(params[1:4])
            self.calc_T(x=params[4], y=params[5], z=params[6])

        _RT = np.hstack([self.R, self.T])
        _AT_inv = np.linalg.inv(self.A @ _RT)
        _new_point = _AT_inv @ point_image.get_image_full()
        point_real = Point.copy(point_image)
        point_real.set_real(_new_point)
        return point_real
