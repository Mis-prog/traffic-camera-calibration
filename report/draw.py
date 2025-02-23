import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from scipy.spatial.transform import Rotation


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
    ax.set_xlim(-10, 30)
    ax.set_ylim(0, 30)

    return ax


def plot_axies(position, angles=[]):
    if not angles:
        ax.quiver(*position, 9, 0, 0, color='black')
        ax.quiver(*position, 0, 6, 0, color='black')
        ax.quiver(*position, 0, 0, 6, color='black')
        text_size = 12
        ax.text(position[0] + 9, position[1] + 1, position[2], 'X', color='black', fontsize=text_size)
        ax.text(position[0], position[1] + 6.5, position[2], 'Y', color='black', fontsize=text_size)
        ax.text(position[0], position[1], position[2] + 6.5, 'Z', color='black', fontsize=text_size)
    else:
        rot = Rotation.from_euler('zxy', angles, degrees=True).as_matrix()
        transform = np.eye(4)
        transform[:3, :3] = rot
        transform[:3, 3] = -rot @ position

        x_position = transform @ np.array([9, 0, 0, 1])
        y_position = transform @ np.array([0, 6, 0, 1])
        z_position = transform @ np.array([0, 0, 6, 1])
        origin = transform @ np.array([0, 0, 0, 1])
        # print(f'Положение камеры:\nx: {x_position[:-1]}\ny: {y_position[:-1]}\nz: {z_position[:-1]}')
        point = transform @ origin
        distances = np.sqrt(np.sum(point[:3] ** 2))
        print(f'Расстояние до точки {distances}')

        ax.quiver(*origin[:-1], *(x_position[:-1] - origin[:-1]), color='black')
        ax.quiver(*origin[:-1], *(y_position[:-1] - origin[:-1]), color='black')
        ax.quiver(*origin[:-1], *(z_position[:-1] - origin[:-1]), color='black')
        text_size = 12
        ax.text(*x_position[:-1], 'X', color='black', fontsize=text_size)
        ax.text(*y_position[:-1], 'Y', color='black', fontsize=text_size)
        ax.text(*z_position[:-1], 'Z', color='black', fontsize=text_size)


def plot_line(lines):
    for line in lines:
        # print(line[0])
        # plt.scatter(x_values, y_values, color='black')  #
        plt.plot(*line, color='black')


h = 30
ax = init(h)
plot_axies([0, 0, 0])
plot_axies([0, 0, h], [-99.58434695, 37.91236625, -167.6947188])

lines = [[[i, 10 * i + 10], [i + 10, 10 * i + 10]] for i in range(2)]
# print(lines)
plot_line(lines)
plt.show()
