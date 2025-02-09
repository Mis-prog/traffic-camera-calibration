import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from scipy.spatial.transform import Rotation


def euler_to_rotation_matrix(angles):
    rot = Rotation.from_euler('zxy', angles, degrees=True)
    return rot.as_matrix()


camera_position = np.array([0, 0, 30])


def plot_camera_orientation(rotation_matrix, position):
    # Вектор, который будет направлением камеры
    direction = np.dot(rotation_matrix, np.array([0, 0, 3]))  # Камера изначально направлена вдоль оси Z

    # Настроим график
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Начальная позиция камеры (центр координат)
    ax.quiver(position[0], position[1], position[2], direction[0], direction[1], direction[2], color='r',
              label='Camera Direction')

    # Оси X, Y, Z от позиции камеры
    ax.quiver(position[0], position[1], position[2], 1, 0, 0, color='g', alpha=0.5, label='X axis (Camera)')
    ax.quiver(position[0], position[1], position[2], 0, 1, 0, color='b', alpha=0.5, label='Y axis (Camera)')
    ax.quiver(position[0], position[1], position[2], 0, 0, 1, color='y', alpha=0.5, label='Z axis (Camera)')

    # Мировые оси (начинаются в точке (0, 0, 0))
    ax.quiver(0, 0, 0, 5, 0, 0, color='g', label='X axis (World)')
    ax.quiver(0, 0, 0, 0, 5, 0, color='b', label='Y axis (World)')
    ax.quiver(0, 0, 0, 0, 0, 5, color='y', label='Z axis (World)')

    # Настройки графика
    ax.set_xlim([0, 5])
    ax.set_ylim([0, 5])
    ax.set_zlim([0, 33])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    plt.show()


angles = [-167, 0, 0]
rotation_matrix = euler_to_rotation_matrix(angles)
plot_camera_orientation(rotation_matrix, camera_position)
