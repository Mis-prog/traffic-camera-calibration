import numpy as np
from scipy.spatial.transform import Rotation


class CameraExtrinsics:
    def __init__(self):
        self.R = np.eye(3)
        self.C = np.array([0, 0, 10])

    def set_rotation(self, data, from_type='euler'):
        if from_type == 'euler':
            self.R = Rotation.from_euler('zxy', data, degrees=True).as_matrix()
        elif from_type == 'vp':
            if data.shape == (3, 3):
                self.R = data
            else:
                raise ValueError("Ожидается матрица 3x3 для from_type='vp'")
        else:
            raise ValueError("Неверный тип ориентации")

    def set_position(self, x=0, y=0, z=10):
        self.C = np.array([x, y, z])

    def get_rotation(self):
        return self.R

    def get_angles(self, order='zxy', degrees=True):
        """
        :return: (rz, rx, ry)
        """
        return Rotation.from_matrix(self.R).as_euler(order, degrees=degrees)

    def get_position(self):
        return tuple(float(c) for c in np.ravel(self.C))

    def get(self):
        t = -self.R @ self.C
        RT = np.hstack([self.R, t.reshape(3, 1)])
        return RT
