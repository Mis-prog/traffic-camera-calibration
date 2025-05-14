import numpy as np
from scipy.spatial.transform import Rotation


class CameraExtrinsics:
    def __init__(self):
        self.R = np.eye(3)
        self.C = np.zeros((3, 1))

    def set_rotation(self, data, from_type='euler'):
        if from_type == 'euler':
            self.R = Rotation.from_euler('zxy', data, degrees=True).as_matrix()
        elif from_type == 'vp': # надо умножить на K_inv перед этим
            vx, vy, vz = map(lambda v: v / np.linalg.norm(v), data)
            self.R = np.stack([vx, vy, vz], axis=1)
        else:
            raise ValueError("Неверный тип ориентации")

    def set_position(self, x=0, y=0, z=0):
        self.C = np.array([[x], [y], [z]])

    def get_rotation(self):
        return self.R

    def get_position(self):
        return self.C

    def get(self):
        t = -self.R @ self.C
        RT = np.hstack([self.R, t])
        return RT
