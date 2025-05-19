import numpy as np
from calibration.base import Calibration
from source.core import Camera

class VanishingPointCalibration(Calibration):
    def __init__(self, camera: Camera, debug=False):
        super().__init__(camera)
        self.vpX = None  # точка схода по оси X (горизонт)
        self.vpY = None  # точка схода по оси Y (горизонт)
        self.vpZ = None  # точка схода по оси Z (вертикаль)
        self.debug = debug

    def set_vanishing_points(self, vpX, vpY=None, vpZ=None):
        self.vpX = np.array(vpX, dtype=float)
        if vpY is not None:
            self.vpY = np.array(vpY, dtype=float)
        if vpZ is not None:
            self.vpZ = np.array(vpZ, dtype=float)

    def calc_f(self):
        if self.vpX is None or self.vpZ is None:
            raise ValueError("vpX и vpZ обязательны для расчета фокусного расстояния.")

        v1 = np.append(self.vpX, 1.0)
        v2 = np.append(self.vpZ, 1.0)
        cx, cy = self.camera.intrinsics.get_main_point()
        c = np.array([cx, cy, 1.0])

        term = np.dot(v1 - c, c - v2)
        if term <= 0:
            raise ValueError("Подкоренное выражение отрицательно. Проверь точки схода.")

        f = np.sqrt(term)
        return f

    def calc_R(self, f):
        self.camera.intrinsics.set_focal_length(f)
        K_inv = np.linalg.inv(self.camera.intrinsics.get())

        dx = K_inv @ np.append(self.vpX, 1.0)
        dz = K_inv @ np.append(self.vpZ, 1.0)

        dy = None
        if self.vpY is not None:
            dy = K_inv @ np.append(self.vpY, 1.0)

        return self._build_rotation(dx, dy, dz)

    def _build_rotation(self, dx, dy, dz):
        # Нормируем
        x = dx / np.linalg.norm(dx)
        z = dz / np.linalg.norm(dz)

        # Если есть Y, уточняем систему
        if dy is not None:
            y = dy / np.linalg.norm(dy)

            x = np.cross(y, z)
            x /= np.linalg.norm(x)
            y = np.cross(z, x)
            y /= np.linalg.norm(y)
        else:
            y = np.cross(z, x)
            y /= np.linalg.norm(y)

        # Собираем R: столбцы — оси X, Y, Z в координатах камеры
        R = np.column_stack((x, y, z))
        return R

    def run(self, data=None, **kwargs):
        """
        Выполняет инициализацию параметров камеры по точкам схода.
        :return: обновлённая камера
        """
        print("[VP Init] Start init ...")

        f = self.calc_f()
        print(f"[VP Init] Focal lenght: {f}")
        R = self.calc_R(f)

        self.camera.extrinsics.set_rotation(R, from_type='vp')
        angle = self.camera.extrinsics.get_angles()
        print(f"[VP Init] Angles ZXY : {angle}")

        print("[VP Init] Done")

        if self.debug:
            from calibration.debug import visualize_vanishing_point_debug
            visualize_vanishing_point_debug(self.camera)
        return self.camera
