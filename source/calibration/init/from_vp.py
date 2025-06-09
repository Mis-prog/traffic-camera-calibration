import numpy as np
from ..base import Calibration
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
        cx, cy = self.camera.intrinsics.get_main_point()
        c = np.array([cx, cy, 1.0])

        if self.vpX is not None and self.vpZ is not None:
            v1 = np.append(self.vpX, 1.0)
            v2 = np.append(self.vpZ, 1.0)

            term = np.dot(v1 - c, c - v2)
            if term <= 0:
                raise ValueError("Подкоренное выражение отрицательно. Проверь точки схода.")

            f = np.sqrt(term)
            return f

        elif self.vpX is not None and self.vpY is not None:
            v1 = np.append(self.vpX, 1.0)
            v2 = np.append(self.vpY, 1.0)

            term = np.dot(v1 - c, c - v2)
            if term <= 0:
                raise ValueError("Подкоренное выражение отрицательно. Проверь точки схода.")

            f = np.sqrt(term)
            return f

    def calc_R(self, f):
        self.camera.intrinsics.set_focal_length(f)
        K_inv = np.linalg.inv(self.camera.intrinsics.get())

        dx = K_inv @ np.append(self.vpX, 1.0)
        dy = K_inv @ np.append(self.vpY, 1.0) if self.vpY is not None else None
        dz = K_inv @ np.append(self.vpZ, 1.0) if self.vpZ is not None else None

        return self._build_rotation(dx, dy, dz)

    def _build_rotation(self, dx, dy, dz):
        # Нормируем
        x = dx / np.linalg.norm(dx)

        if dy is not None and dz is not None:
            y = dy / np.linalg.norm(dy)
            z = dz / np.linalg.norm(dz)

            # Ортонормализация: перестроим Y и Z так, чтобы система была ортогональна
            z = z - np.dot(z, x) * x - np.dot(z, y) * y
            z /= np.linalg.norm(z)

            y = np.cross(z, x)
            y /= np.linalg.norm(y)
        elif dy is None:
            z = dz / np.linalg.norm(dz)
            # Если Y не был задан — восстановим его
            y = np.cross(z, x)
            y /= np.linalg.norm(y)

        elif dz is None:
            y = dy / np.linalg.norm(dy)
            # Если Z не был задан — восстановим его
            z = np.cross(x, y)
            z /= np.linalg.norm(z)

        else:
            raise ValueError("В сцене только одна точка схода. Проверь точки схода.")

        # Собираем R: столбцы — оси X, Y, Z в координатах камеры
        R = np.column_stack((x, y, z))

        z = R[:, 2]

        if z[2] > 0:  # например, камера "смотрит вверх" — это неправильно
            print("[VP Init] ⚠️ Камера смотрит назад — инвертируем ориентацию")
            R[:, 2] *= -1
            R[:, 1] = np.cross(R[:, 2], R[:, 0])
            R[:, 1] /= np.linalg.norm(R[:, 1])

        print(f' [VP Init] Determinant(R): {np.linalg.det(R)}')
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
        print("=" * 50)
        print("🎯 [VP Init] Инициализация параметров по точкам схода")
        print("=" * 50)

        f = self.calc_f()
        print(f"🔬 Вычислено фокусное расстояние: f = {f:.4f}")

        R = self.calc_R(f)

        self.camera.extrinsics.set_rotation(R, from_type='vp')
        angles = self.camera.extrinsics.get_angles()
        print(f"🧭 Углы ориентации (ZXY, град): {np.round(angles, 2)}")
        print("✅ [VP Init] Инициализация завершена")

        if self.debug_save_path is not None:
            from source.calibration.debug import visualize_vps_debug
            print(f"💾 Сохраняю визуализацию в: {self.debug_save_path}")
            visualize_vps_debug(self.camera, save_path=self.debug_save_path)

        print("=" * 50)
        return self.camera
