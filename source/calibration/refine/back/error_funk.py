import numpy as np

from core import Camera, PointND


def residual_interline_distance(camera, data, group, expected):
    residuals = []
    lines = data.get(group, [])
    for i in range(len(lines) - 1):
        d = compute_interline_distance(camera, lines[i], lines[i + 1])
        residuals.append(d - expected)
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
