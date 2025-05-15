import cv2
import numpy as np

from .camera_intrinsics import CameraIntrinsics
from .camera_extrinsics import CameraExtrinsics
from .pointND import PointND


class Camera:
    def __init__(self, path_image):
        self.image = cv2.imread(path_image)
        self.size = self.image.shape[:2]
        self.path = path_image

        self.intrinsics = CameraIntrinsics(self.size[1], self.size[0])
        self.extrinsics = CameraExtrinsics()

    def set_params(self, params: dict):
        """
        Устанавливает параметры камеры из словаря.

        Ожидаемые ключи:
            - f или (fx, fy): фокусное расстояние (одно или два)
            - rz, rx, ry: углы Эйлера в градусах (если from_type='euler')
            - vp: список из трёх направлений (если from_type='vp')
            - x, y, z: координаты положения камеры
            - from_type: 'euler' или 'vp'
        """
        # --- фокус ---
        if "f" in params:
            self.intrinsics.set_focal_length(params["f"])
        elif "fx" in params and "fy" in params:
            self.intrinsics.set_focal_length((params["fx"], params["fy"]))
        else:
            raise ValueError("Отсутствует фокусное расстояние (f или fx/fy)")

        # --- ориентация ---
        from_type = params.get("from_type", "euler")
        if from_type == "euler":
            angles = [params.get("rz", 0), params.get("rx", 0), params.get("ry", 0)]
            self.extrinsics.set_rotation(angles, from_type="euler")
        elif from_type == "vp":
            vp_list = params.get("vp")
            if vp_list is None or len(vp_list) != 3:
                raise ValueError("Для from_type='vp' нужно три вектора vp")
            self.extrinsics.set_rotation(vp_list, from_type="vp")
        else:
            raise ValueError(f"Неизвестный тип from_type: {from_type}")

        # --- позиция ---
        x = params.get("x", 0)
        y = params.get("y", 0)
        z = params.get("z", 0)
        self.extrinsics.set_position(x, y, z)

    def get_image(self):
        return self.image

    def get_size(self):
        return self.size

    def project_direct(self, point3D: PointND) -> PointND:
        RT = self.extrinsics.get()
        K = self.intrinsics.get()
        P = K @ RT
        point2D = PointND(P @ point3D.get(out_homogeneous=True), add_weight=True)
        return point2D

    def project_back(self, point2D: PointND) -> PointND:
        pass

    def homography(self, point: PointND, direction='direct') -> PointND:
        RT = self.extrinsics.get()
        RT = np.delete(RT, 2, axis=1)  # удаляем третий столбец (оси Z) ⇒ проекция на плоскость Z=0
        H = self.intrinsics.get() @ RT  # Гомография

        p = point.get(out_homogeneous=True)
        if direction == 'direct':
            transformed = H @ p
        elif direction == 'back':
            H_inv = np.linalg.inv(H)
            transformed = H_inv @ p
        else:
            raise ValueError("Аргумент direction должен быть 'direct' или 'back'.")

        return PointND(transformed, add_weight=False)
