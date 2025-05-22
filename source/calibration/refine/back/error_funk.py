import numpy as np

from core import Camera, PointND


def target_residuals_lsq(camera: Camera, data: dict, params: list) -> np.ndarray:
    camera.set_params_from_list(params)
    residuals = []
    if "dist_between_line" in data:
        for i in range(len(data["dist_between_line"]) - 1):
            line1 = data["dist_between_line"][i]
            line2 = data["dist_between_line"][i + 1]
            dist = compute_interline_distance(camera, line1, line2)

    return np.array(residuals)


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
