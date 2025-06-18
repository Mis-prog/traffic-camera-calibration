import cv2
import numpy as np

from .camera_intrinsics import CameraIntrinsics
from .camera_extrinsics import CameraExtrinsics
from .pointND import PointND


class Camera:
    def __init__(self, path_image=None, size=None):
        if path_image is not None:
            self.image = cv2.cvtColor(cv2.imread(path_image), cv2.COLOR_BGR2RGB)
            self.size = self.image.shape[:2]  # (height, width)
            self.path = path_image
        elif size is not None:
            self.image = None
            self.size = size  # size = (height, width)
            self.path = None
        else:
            raise ValueError("Нужно указать либо path_image, либо size")

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

    def set_params_from_list(self, param_list: list):
        """
        Устанавливает параметры камеры из плоского списка.
        Ожидается формат: [f, rz, rx, ry, x, y, z]
        """
        if len(param_list) != 7:
            raise ValueError("Ожидается 7 параметров: f, rz, rx, ry, x, y, z")

        f = param_list[0]
        rz, rx, ry = param_list[1:4]
        x, y, z = param_list[4:7]

        self.intrinsics.set_focal_length(f)
        self.extrinsics.set_rotation([rz, rx, ry], from_type="euler")
        self.extrinsics.set_position(x, y, z)

    def get_params(self) -> list:
        params = []

        f = self.intrinsics.get_focal_length()
        if isinstance(f, tuple):  # fx, fy
            params.extend(f)
        else:
            params.append(f)

        rz, rx, ry = self.extrinsics.get_angles()
        params.extend([rz, rx, ry])

        x, y, z = self.extrinsics.get_position()
        assert isinstance(x, float)
        params.extend([x, y, z])

        return params

    def get_image(self):
        return self.image

    def get_size(self):
        return self.size

    def project_direct(self, point3D: PointND) -> PointND:
        RT = self.extrinsics.get()
        K = self.intrinsics.get()
        P = K @ RT
        point2D = PointND(P @ point3D.get(out_homogeneous=True), add_weight=False)
        return point2D

    def project_back(self, point2D: PointND, plane_z: float = 0.0) -> PointND:
        K = self.intrinsics.get()
        R = self.extrinsics.get_rotation()
        C = np.array(self.extrinsics.get_position())

        x = point2D.get(out_homogeneous=True)

        # Направление луча в системе мира
        K_inv = np.linalg.inv(K)
        ray_cam = K_inv @ x  # направление в системе камеры
        ray_world = R.T @ ray_cam  # в мировой системе координат

        # Нормализуем направление (не обязательно, но можно)
        ray_world = ray_world / np.linalg.norm(ray_world)

        # Параметрическое пересечение с плоскостью Z = plane_z
        t = (plane_z - C[2]) / ray_world[2]  # ищем такой t, чтобы Z == plane_z
        point3D = C + t * ray_world  # точка на плоскости

        return PointND(point3D, add_weight=True)

    def backproject_ray(self, pixel_2d: tuple[float, float]) -> np.ndarray:
        """
        Возвращает направляющий вектор луча, проходящего от центра камеры через пиксель.
        В мировой системе координат.
        """
        K = self.intrinsics.get()
        R = self.extrinsics.get_rotation()

        # Преобразуем пиксель в однородные координаты
        x = np.array([pixel_2d[0], pixel_2d[1], 1.0])

        # Направление в камере
        ray_cam = np.linalg.inv(K) @ x

        # Направление в мировой системе
        ray_world = R.T @ ray_cam
        ray_world /= np.linalg.norm(ray_world)

        return ray_world


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
