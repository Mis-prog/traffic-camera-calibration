import numpy as np
from calibration.base import Calibration
from source.core import Camera, PointND


class VanishingPointCalibration(Calibration):
    def __init__(self, camera: Camera, debug_save_path: str = None):
        super().__init__(camera, debug_save_path)
        self.vpX = None  # точка схода по оси X (горизонт)
        self.vpY = None  # точка схода по оси Y (горизонт)
        self.vpZ = None  # точка схода по оси Z (вертикаль)

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

        if dy is not None:
            y = dy / np.linalg.norm(dy)

            # Ортонормализация: перестроим Y и Z так, чтобы система была ортогональна
            z = z - np.dot(z, x) * x - np.dot(z, y) * y
            z /= np.linalg.norm(z)

            y = np.cross(z, x)
            y /= np.linalg.norm(y)
        else:
            # Если Y не был задан — восстановим его
            y = np.cross(z, x)
            y /= np.linalg.norm(y)

        # Собираем R: столбцы — оси X, Y, Z в координатах камеры
        R = np.column_stack((x, y, z))
        return R

    # def _build_rotation(self, dx, dy, dz):
    #     # Нормализуем исходные направления
    #     x = dx / np.linalg.norm(dx)
    #     z = dz / np.linalg.norm(dz)
    #
    #     if dy is not None:
    #         y = dy / np.linalg.norm(dy)
    #
    #         # Корректируем y, чтобы она была ортогональна x и z
    #         # Сначала получаем "правильную" y из x и z
    #         y_proj = np.cross(z, x)
    #         y_proj /= np.linalg.norm(y_proj)
    #
    #         # Уточняем x, чтобы он был ортогонален y_proj и z
    #         x = np.cross(y_proj, z)
    #         x /= np.linalg.norm(x)
    #
    #         # Пересобираем y ещё раз — теперь она точно ортогональна x и z
    #         y = np.cross(z, x)
    #         y /= np.linalg.norm(y)
    #     else:
    #         # Если Y не задан, достраиваем правую тройку
    #         y = np.cross(z, x)
    #         y /= np.linalg.norm(y)
    #
    #     # Собираем матрицу поворота R: [x_cam, y_cam, z_cam]
    #     R = np.column_stack((x, y, z))

    # Проверим, что R правая: det ≈ +1
    # if np.linalg.det(R) < 0:
    #     # Например, инвертируем y (или x), чтобы восстановить ориентацию
    #     y = -y
    #     R = np.column_stack((x, y, z))
    #
    # return R

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

        if self.debug_save_path is not None:
            from calibration.debug import visualize_vps_debug
            visualize_vps_debug(self.camera, save_path=self.debug_save_path)

        return self.camera
