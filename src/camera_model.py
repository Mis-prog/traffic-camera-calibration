import numpy as np
import cv2
from scipy.spatial.transform import Rotation
from .point2D import Point2D
from .point3D import Point3D


class Camera:
    def __init__(self):
        self.size = None
        self.scene = None
        self.tau = None
        self.f = None
        self.path = None

        self.A = np.zeros((3, 3))
        self.R = np.zeros((3, 3))
        self.T = np.zeros((3, 1)).reshape(-1, 1)

    def set_params(self, params):
        if len(params) == 5:
            self.calc_A(params[0])
            self.calc_R(params[1:4])
            self.calc_T(z=params[4])
        elif len(params) == 7:
            self.calc_A(params[0])
            self.calc_R(params[1:4])
            self.calc_T(x=params[4], y=params[5], z=params[6])

    def get_scene(self):
        return self.scene

    def get_f(self):
        return self.f

    def get_tau(self):
        return self.tau

    def calc_tau(self, height, width):
        self.size = [height, width]  # высота и ширина
        self.tau = height / width

    def load_scene(self, path):
        self.path = path
        self.scene = cv2.imread(path)
        height, width, channels = self.scene.shape
        # print(height,width)
        self.calc_tau(height, width)

    # вычисление матрицы поворота
    def calc_R(self, euler_angles):
        rot = Rotation.from_euler('zxy', euler_angles, degrees=True)
        self.R = rot.as_matrix()

    def set_init_R(self, p):
        self.R = np.vstack(p).transpose()

    def get_R(self, angle_output=False, output=False):
        if angle_output:
            angles = Rotation.from_matrix(self.R).as_euler('zxy', degrees=True)
            # print(angles)
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
            self.A = np.array([[f, 0, self.size[1] / 2],
                               [0, f * self.tau, self.size[0] / 2],
                               [0, 0, 1]])
            # self.A = np.array([[f, 0, 0],
            #                    [0, f * self.tau, 0],
            #                    [0, 0, 1]])
        else:
            self.A = np.array([[f, 0, self.size[1] / 2],
                               [0, f, self.size[0] / 2],
                               [0, 0, 1]])

    def get_A(self, output=False):
        if output:
            print(f'Внутренние параметры камеры:\n{self.A}')
        return self.A

    # прямое преобразование
    def direct_transform_world(self, point_real: Point3D, params=[]) -> Point2D:
        if len(params) == 5:
            self.calc_A(params[0])
            self.calc_R(params[1:4])
            self.calc_T(z=params[4])

        elif len(params) == 6:
            self.calc_A(params[0])
            self.calc_R(params[1:4])
            self.calc_T(x=params[4], z=params[4])
        elif len(params) == 7:
            self.calc_A(params[0])
            self.calc_R(params[1:4])
            self.calc_T(x=params[4], y=params[5], z=params[6])

        _T1 = -self.R @ self.T
        _RT = np.hstack([self.R, _T1[:, np.newaxis]])
        _AT = self.A @ _RT
        _new_point = Point2D(_AT.dot(point_real.get(out_homogeneous=True)))
        return _new_point

    def direct_transform_camera(self, point_real: Point3D, params=[]) -> Point2D:
        if len(params) == 5:
            self.calc_A(params[0])
            self.calc_R(params[1:4])
            self.calc_T(z=params[4])
        elif len(params) == 6:
            self.calc_A(params[0])
            self.calc_R(params[1:4])
            self.calc_T(x=params[4], z=params[4])
        elif len(params) == 7:
            self.calc_A(params[0])
            self.calc_R(params[1:4])
            self.calc_T(x=params[4], y=params[5], z=params[6])

        _new_point = Point2D(self.A @ point_real.get())
        return _new_point

    def back_transform_world(self, point_image: Point2D, params=[]) -> Point2D:
        if len(params) == 5:
            self.calc_A(params[0])
            self.calc_R(params[1:4])
            self.calc_T(z=params[4])
        elif len(params) == 7:
            self.calc_A(params[0])
            self.calc_R(params[1:4])
            self.calc_T(x=params[4], y=params[5], z=params[6])

        _T1 = -self.R @ self.T
        _RT = np.hstack([self.R, _T1[:, np.newaxis]])
        _RT = np.delete(_RT, 2, axis=1)
        _AT = self.A @ _RT
        _AT_inv = np.linalg.inv(_AT)
        _new_point = Point2D(_AT_inv @ point_image.get(out_homogeneous=True))
        return _new_point