import numpy as np
from scipy.spatial.transform import Rotation as R

from source.core import Camera, PointND


def residual_interline_distance(camera, data, group, expected):
    residuals = []
    lines = data.get(group, [])
    for i in range(len(lines) - 1):
        d = compute_interline_distance(camera, lines[i], lines[i + 1])
        # print(f"[DEBUG] d={d:.2f} (expected {expected:.2f}) delta={d - expected:.3f}")
        residuals.append(np.abs(d - expected))
    return residuals


def compute_interline_distance(camera: Camera, line1, line2, plane_z=0):
    c1 = PointND(np.mean(line1, axis=0))
    c2 = PointND(np.mean(line2, axis=0))

    X1 = camera.project_back(c1, plane_z).get()
    X2 = camera.project_back(c2, plane_z).get()

    # аппроксимируем направление по первой линии
    P1a = camera.project_back(PointND(line1[0]), plane_z).get()
    P1b = camera.project_back(PointND(line1[1]), plane_z).get()
    direction = P1b - P1a
    direction = direction[:2] / np.linalg.norm(direction[:2])
    normal = np.array([-direction[1], direction[0]])  # ортогонально в 2D

    # проецируем разность точек на нормаль
    delta = (X2 - X1)[:2]
    dist = np.abs(np.dot(delta, normal))
    return dist


def residual_parallel_group(camera, data, group, plane_z=0):
    """
    Резидуал: проверяет, что все линии в группе параллельны в мировой системе координат.
    Ошибка = косое произведение направляющих векторов.

    :param camera: модель камеры
    :param data: словарь с линиями
    :param group: имя ключа в data
    :param plane_z: плоскость обратной проекции
    :return: список residuals
    """
    residuals = []
    lines = data.get(group, [])

    if len(lines) < 2:
        return residuals  # нечего сравнивать

    # вычисляем 3D-направляющие
    directions = []
    for p1, p2 in lines:
        X1 = camera.project_back(PointND(p1), plane_z).get()
        X2 = camera.project_back(PointND(p2), plane_z).get()
        d = X2 - X1
        norm = np.linalg.norm(d)
        if norm < 1e-6:
            continue  # вырожденная
        directions.append(d[:2] / norm)  # только XY-плоскость

    if len(directions) < 2:
        return residuals  # не хватает направлений

    # сравниваем каждую с первой
    ref = directions[0]
    for d in directions[1:]:
        cross = np.cross(ref, d)  # → 0, если параллельны
        residuals.append(cross)

    return residuals


def compute_line_length(camera: Camera, line, plane_z=0):
    """
    Возвращает длину линии в 3D, восстановленной из двух концов.
    """
    P1 = camera.project_back(PointND(line[0]), plane_z).get()
    P2 = camera.project_back(PointND(line[1]), plane_z).get()
    return np.linalg.norm(P2 - P1)


def residual_line_length(camera, data, group, expected):
    """
    Возвращает список остатков (residuals), включающий:
    - отклонения расстояний между линиями от expected_spacing
    - отклонения длин линий от expected_length
    """
    residuals = []
    lines = data.get(group, [])

    # Длины самих линий
    for line in lines:
        L = compute_line_length(camera, line, 0)
        residuals.append(np.abs(L - expected))

    return residuals


def residual_orthogonality_error(camera, data, group):
    residuals = []
    lines = data.get(group, [])

    for (p1, p2), (q1, q2) in lines:
        # Проецируем точки на изображение
        p1_world = camera.project_back(PointND(p1)).get()
        p2_world = camera.project_back(PointND(p2)).get()
        q1_world = camera.project_back(PointND(q1)).get()
        q2_world = camera.project_back(PointND(q2)).get()

        # Направляющие векторы
        v1 = p2_world - p1_world
        v2 = q2_world - q1_world

        # Нормализация (чтобы убрать влияние длины)
        v1 /= np.linalg.norm(v1)
        v2 /= np.linalg.norm(v2)

        # Скалярное произведение: должно быть 0 при 90°
        dot = np.dot(v1, v2)

        # Ошибка — квадрат скалярного произведения
        residuals.append(dot ** 2)

    return residuals


def residual_planar_alignment(omega, R0, K, planar_lines_img):
    delta_R = R.from_rotvec(omega).as_matrix()
    R_corr = delta_R @ R0
    K_inv = np.linalg.inv(K)

    residuals = []
    for line_dir in planar_lines_img:
        line_dir = line_dir / np.linalg.norm(line_dir)
        dir_img_h = np.array([line_dir[0], line_dir[1], 1.0])
        dir_cam = K_inv @ dir_img_h
        dir_cam = dir_cam / np.linalg.norm(dir_cam)
        dir_world = R_corr.T @ dir_cam
        z_component = dir_world[2]
        residuals.append(z_component)  # просто сама компонента, без квадрата
    return residuals


def residual_vertical_alignment(omega, R0, K, lines_img):
    delta_R = R.from_rotvec(omega).as_matrix()
    R_corr = delta_R @ R0
    z_world = np.array([0, 0, 1])

    residuals = []
    for line_dir in lines_img:
        line_dir = line_dir / np.linalg.norm(line_dir)
        v_cam = R_corr @ z_world
        v_img = K @ v_cam
        v_img = v_img[:2] / v_img[2]
        v_img = v_img / np.linalg.norm(v_img)
        cos_theta = np.dot(v_img, line_dir)
        residuals.append(1 - cos_theta ** 2)
    return residuals


def residual_alignment_block(verticals=None, planar_lines=None, weights=(1.0, 1.0, 10.0)):
    """
    Возвращает residual-функцию совместимую с RefineOptimizer:
    (camera, data) -> List[float]
    """

    def block(camera, data):
        # Начальное приближение (ориентация R0 фиксируется при создании блока)
        angles_current = camera.get_params()[1:4]
        R_current = R.from_euler('zyx', angles_current, degrees=True)

        # Предположим, что R0 зафиксировано в момент создания блока
        # → сохраним его в момент инициализации
        if not hasattr(block, "_R0"):
            block._R0 = R_current
            block._angles0 = angles_current

        R0 = block._R0.as_matrix()
        R1 = R_current.as_matrix()

        # Разность вращений
        R_delta = R1 @ R0.T
        omega = R.from_matrix(R_delta).as_rotvec()

        residuals = []
        if verticals:
            res_vert = residual_vertical_alignment(omega, R0, camera.intrinsics.get(), verticals)
            residuals.extend([weights[0] * r for r in res_vert])
        if planar_lines:
            res_planar = residual_planar_alignment(omega, R0, camera.intrinsics.get(), planar_lines)
            residuals.extend([weights[1] * r for r in res_planar])

        residuals.extend([weights[2] * w for w in omega])
        return residuals

    return block
