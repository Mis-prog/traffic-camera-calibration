from calibration_new.base import Calibration
from core.camera import Camera
import numpy as np


class InitFromVanishingPoints(Calibration):
    def run(self, camera: Camera, vps: np.ndarray) -> Camera:
        """
        vps — список из 2 или 3 точек схода: [vpX, vpZ] или [vpX, vpY, vpZ]
        """
        if len(vps) < 2:
            raise ValueError("Необходимо как минимум 2 точки схода: vpX и vpZ")

        self.camera = camera  # сохраняем ссылку
        self.vpX = np.array(vps[0], dtype=float)
        self.vpZ = np.array(vps[1], dtype=float)
        self.vpY = np.array(vps[2], dtype=float) if len(vps) == 3 else None

        cx, cy = self.camera.intrinsics.get_main_point()

        # 1. Вычисляем фокусное расстояние
        f = self.calc_f(self.vpX, self.vpZ)
        self.camera.intrinsics.set_focal_length(f)

        # 2. Вычисляем матрицу поворота
        R = self.calc_R(f)
        self.camera.extrinsics.set_rotation(R)

        return self.camera

    def calc_f(self, vpX, vpZ) -> float:
        if vpX is None or vpZ is None:
            raise ValueError("vpX и vpZ обязательны для расчета фокусного расстояния.")

        v1 = np.append(vpX, 1.0)
        v2 = np.append(vpZ, 1.0)
        cx, cy = self.camera.intrinsics.get_main_point()
        c = np.array([cx, cy, 1.0])

        term = np.dot(v1 - c, c - v2)
        if term <= 0:
            raise ValueError("Подкоренное выражение отрицательно. Проверь точки схода.")

        return np.sqrt(term)

    def calc_R(self, f: float) -> np.ndarray:
        self.camera.intrinsics.set_focal_length(f)
        K_inv = np.linalg.inv(self.camera.intrinsics.get())

        dx = K_inv @ np.append(self.vpX, 1.0)
        dz = K_inv @ np.append(self.vpZ, 1.0)
        dy = K_inv @ np.append(self.vpY, 1.0) if self.vpY is not None else None

        return self._build_rotation(dx, dy, dz)

    def _build_rotation(self, dx, dy, dz) -> np.ndarray:
        x = dx / np.linalg.norm(dx)
        z = dz / np.linalg.norm(dz)

        if dy is not None:
            y = dy / np.linalg.norm(dy)
            z = np.cross(x, y)
            z /= np.linalg.norm(z)
            y = np.cross(z, x)
        else:
            y = np.cross(z, x)
            y /= np.linalg.norm(y)

        return np.column_stack((x, y, z))
