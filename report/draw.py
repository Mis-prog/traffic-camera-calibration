import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np


def init():
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

    # ax.set_proj_type('persp')

    ax.set_zlim(0, 30)
    ax.set_xlim([-10, 30])
    ax.set_ylim([0, 30])

    return ax


ax = init()


def plot_axies(position, meas):
    ax.quiver(*position, 9, 0, 0, color='black')
    ax.quiver(*position, 0, 6, 0, color='black')
    ax.quiver(*position, 0, 0, 6, color='black')
    text_size = 12  # Одинаковый размер шрифта
    ax.text(9, 0, 0, 'X', color='black', fontsize=text_size)
    ax.text(0, 6, 0, 'Y', color='black', fontsize=text_size)
    ax.text(0, 0, 6, 'Z', color='black', fontsize=text_size)


# Рисуем стрелки для осей X, Y и Z
plot_axies([0, 0, 0], 10)

plt.show()
