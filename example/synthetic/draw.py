import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from scipy.spatial.transform import Rotation

from src.camera_model import Camera
from src.pointND import PointND
from src.new_optimization import NewOptimization


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
    ax.set_xlim(-60, 60)
    ax.set_ylim(-60, 60)

    return ax


def plot_axies(position, angles=[]):
    if not angles:
        ax.quiver(*position, 15, 0, 0, color='black')
        ax.quiver(*position, 0, 15, 0, color='black')
        ax.quiver(*position, 0, 0, 15, color='black')
        ax.scatter(0, 0, 0, marker='^', s=100, color='red', label='Мировая система координат')
        text_size = 12
        ax.text(position[0] + 15, position[1] + 1, position[2], 'X', color='black', fontsize=text_size)
        ax.text(position[0], position[1] + 15, position[2], 'Y', color='black', fontsize=text_size)
        ax.text(position[0], position[1], position[2] + 15, 'Z', color='black', fontsize=text_size)
    else:
        rot = Rotation.from_euler('zxy', angles, degrees=True).as_matrix()
        transform = np.eye(4)
        transform[:3, :3] = rot
        transform[:3, 3] = -rot @ position
        x_position = transform @ np.array([15, 0, 0, 1])
        y_position = transform @ np.array([0, 15, 0, 1])
        z_position = transform @ np.array([0, 0, 15, 1])
        origin = transform @ np.array([0, 0, 0, 1])
        # print(f'Положение камеры:\nx: {x_position[:-1]}\ny: {y_position[:-1]}\nz: {z_position[:-1]}')
        distances = np.linalg.norm(transform[:3, 3])

        ax.scatter(*transform[:3, 3], color='red', label='Система координат камеры камеры')
        # label=f'{np.around(transform[:3, 3], 2)}, расстонияние до центра {round(distances, 2)}')
        ax.quiver(*origin[:-1], *(x_position[:-1] - origin[:-1]), color='black')
        ax.quiver(*origin[:-1], *(y_position[:-1] - origin[:-1]), color='black')
        ax.quiver(*origin[:-1], *(z_position[:-1] - origin[:-1]), color='black')
        text_size = 12
        ax.text(*x_position[:-1], 'X', color='black', fontsize=text_size)
        ax.text(*y_position[:-1], 'Y', color='black', fontsize=text_size)
        ax.text(*z_position[:-1], 'Z', color='black', fontsize=text_size)

        ax.legend(loc='upper center')


def load_data(path):
    lines = []
    with open(path, 'r') as file:
        for line in file:
            points = eval(line.strip())
            lines.append([PointND([x, y, z]) for x, y, z in points])
    return lines


# эталонные значения
height, width = 700, 1200
h = 40
angles = [189.07, 24.53, -159.51]
f = 920

ax = init(h)
plot_axies([0, 0, 0])
plot_axies([0, 0, h], angles)

for start, end in load_data('data.txt'):
    plt.plot([start.get()[0], end.get()[0]], [start.get()[1], end.get()[1]],  color='black')

plt.show()
