import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from scipy.spatial.transform import Rotation

from src.camera_model import Camera
from src.point3D import Point3D
from src.point2D import Point2D
from src.optimizetion import Optimizer


def init(h):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.zaxis.line.set_color((1.0, 1.0, 1.0, 0.0))  # Ось Z
    ax.xaxis.line.set_color((1.0, 1.0, 1.0, 0.0))  # Ось X
    ax.yaxis.line.set_color((1.0, 1.0, 1.0, 0.0))  # Ось Y

    ax.xaxis.set_tick_params(labelleft=False, labelbottom=False)  # Убираем метки для оси X
    ax.yaxis.set_tick_params(labelleft=False, labelbottom=False)  # Убираем метки для оси Y
    ax.zaxis.set_tick_params(labelleft=False, labelbottom=False)  # Убираем метки для оси Z

    ax.xaxis.set_ticks_position('none')  # Убираем засечки для оси X
    ax.yaxis.set_ticks_position('none')  # Убираем засечки для оси Y
    ax.zaxis.set_ticks_position('none')  # Убираем засечки для оси Z

    # Настройка углов обзора
    ax.view_init(elev=20, azim=30)

    ax.set_proj_type('persp')

    ax.set_zlim(0, h + 10)
    ax.set_xlim(-30, 30)
    ax.set_ylim(-30, 30)

    return ax


def plot_axies(position, angles=[]):
    if not angles:
        ax.quiver(*position, 6, 0, 0, color='black')
        ax.quiver(*position, 0, 6, 0, color='black')
        ax.quiver(*position, 0, 0, 6, color='black')
        text_size = 12
        ax.text(position[0] + 6, position[1] + 1, position[2], 'X', color='black', fontsize=text_size)
        ax.text(position[0], position[1] + 6, position[2], 'Y', color='black', fontsize=text_size)
        ax.text(position[0], position[1], position[2] + 6, 'Z', color='black', fontsize=text_size)
    else:
        rot = Rotation.from_euler('zxy', angles, degrees=True).as_matrix()
        transform = np.eye(4)
        transform[:3, :3] = rot
        transform[:3, 3] = -rot @ position
        x_position = transform @ np.array([6, 0, 0, 1])
        y_position = transform @ np.array([0, 6, 0, 1])
        z_position = transform @ np.array([0, 0, 6, 1])
        origin = transform @ np.array([0, 0, 0, 1])
        # print(f'Положение камеры:\nx: {x_position[:-1]}\ny: {y_position[:-1]}\nz: {z_position[:-1]}')
        distances = np.linalg.norm(transform[:3, 3])

        ax.scatter(*transform[:3, 3], color='red',
                   label=f'{np.around(transform[:3, 3], 2)}, расстонияние до центра {round(distances, 2)}')
        ax.quiver(*origin[:-1], *(x_position[:-1] - origin[:-1]), color='black')
        ax.quiver(*origin[:-1], *(y_position[:-1] - origin[:-1]), color='black')
        ax.quiver(*origin[:-1], *(z_position[:-1] - origin[:-1]), color='black')
        text_size = 12
        ax.text(*x_position[:-1], 'X', color='black', fontsize=text_size)
        ax.text(*y_position[:-1], 'Y', color='black', fontsize=text_size)
        ax.text(*z_position[:-1], 'Z', color='black', fontsize=text_size)

        ax.legend(loc='upper center')


def world_to_image(params):
    points3D = [[Point3D(start), Point3D(end)] for start, end in POINTS]
    camera = Camera()
    camera.calc_tau(height, width)
    camera.set_params(params)
    points2D = [[camera.direct_transform_world(start), camera.direct_transform_world(end)] for start, end
                in points3D]

    _points = [[start.get(), end.get()] for start, end in points2D]
    _points = np.array(_points)

    return _points


def create_dataset(params):
    camera = Camera()
    camera.calc_tau(height, width)
    camera.set_params(params)

    points_dataset = [
        [(camera.direct_transform_world(Point3D(start)), Point3D(start)),
         (camera.direct_transform_world(Point3D(end)), Point3D(end))]
        for start, end in POINTS]

    return points_dataset


POINTS = np.array([
    [[-10, -20, 0, 1], [-10, 20, 0, 1]],
    [[-5, -20, 0, 1], [-5, 20, 0, 1]],
    [[5, -20, 0, 1], [5, 20, 0, 1]],
    [[10, -20, 0, 1], [10, 20, 0, 1]],
    [[-20, 10, 0, 1], [20, 10, 0, 1]],
    [[-20, -10, 0, 1], [20, -10, 0, 1]],
])


def plot_lines_world():
    for start, end in POINTS:
        plt.plot([start[0], end[0]], [start[1], end[1]], ls='--', color='black')
    plt.axis('equal')
    plt.show()


def plot_lines_image(params):
    _points = world_to_image(params)
    for start, end in _points:
        plt.plot([start[0], end[0]], [start[1], end[1]], ls='--', color='black')
    plt.xlim(0, width)
    plt.ylim(0, height)
    plt.grid()


# эталонные значения
height, width = 300, 700
h = 30
angles = [0, 0, -180]
f = 200
ax = init(h)
plot_axies([0, 0, 0])
plot_axies([0, 0, h], angles)
plot_lines_world()
plot_lines_image([f, *angles, h])
plt.show()

camera = Camera()
camera.calc_tau(height, width)
camera.set_params([f, *angles, h])
optimize = Optimizer(camera)
dataset = create_dataset([f, *angles, h])
camera, info = optimize.optimize_reprojection(dataset)
print(np.around(info.x))
