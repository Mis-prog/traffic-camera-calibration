import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from sympy.physics.units import length

from core import Camera, PointND


def visualize_camera_and_world_axes(
        camera: Camera
):
    """
    Отрисовка системы координат камеры относительно мировой системы координат
    """
    R = camera.extrinsics.get_rotation().T
    C = camera.extrinsics.get_position()
    x_cam = R[:, 0]  # вправо
    y_cam = R[:, 1]  # вверх
    z_cam = R[:, 2]  # взгляд
    scale = 10

    fig = plt.figure(figsize=(8, 8))

    ax = fig.add_subplot(111, projection='3d')

    # Оси мира из начала координат
    ax.quiver(0, 0, 0, 1, 0, 0, length=scale, color='red', label='World X')
    ax.quiver(0, 0, 0, 0, 1, 0, length=scale, color='green', label='World Y')
    ax.quiver(0, 0, 0, 0, 0, 1, length=scale, color='blue', label='World Z')

    ax.quiver(*C, *x_cam, length=scale, color='r', linestyle='dashed', label='Camera X')
    ax.quiver(*C, *y_cam, length=scale, color='g', linestyle='dashed', label='Camera Y')
    ax.quiver(*C, *z_cam, length=scale, color='b', linestyle='dashed', label='Camera Z')

    ax.scatter(*C, label='C')
    ax.scatter(*-R @ C, label='- R @ C')

    point_start = PointND([960, 540])
    plane_z = 0
    grid_range = 10
    grid_step = 1

    anchor_3D = camera.project_back(point_start, plane_z=plane_z)
    anchor_x, anchor_y, anchor_z = anchor_3D.get()

    to_scene = anchor_3D.get() - C

    if np.dot(R[:, 2], to_scene) < 0:
        print("Камера смотрит в обратную сторону — Z нужно инвертировать")

    # Считаем количество узлов в сетке
    count = int(2 * grid_range / grid_step) + 1

    world_points = []
    for i in range(count):
        for j in range(count):
            x = anchor_x - grid_range + i * grid_step
            y = anchor_y - grid_range + j * grid_step
            world_points.append(PointND(np.array([x, y, plane_z])))

    for i in range(count):
        for j in range(count - 1):
            p1 = world_points[i * count + j].get()
            p2 = world_points[i * count + (j + 1)].get()
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='blue', linewidth=1)

    for j in range(count):
        for i in range(count - 1):
            p1 = world_points[i * count + j].get()
            p2 = world_points[(i + 1) * count + j].get()
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='blue', linewidth=1)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Камера и мировая система координат')
    ax.legend()
    plt.tight_layout()
    plt.show()


camera = Camera("../../../example/pushkin_aksakov/image/pattern_corrected_image.png")
camera.set_params_from_list([1230, -13.46, 48.12, -164.54, 0, 0, 10])
# camera.set_params_from_list([1246.66, -142.93, 49.25, 173.98, -10.02, -15.42, 27.31])
visualize_camera_and_world_axes(camera)
