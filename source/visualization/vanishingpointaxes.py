from abc import ABC

import numpy as np
import matplotlib.pyplot as plt
import cv2

from .drawable import Drawable


class VanishingPointAxes(Drawable):
    def __init__(self):
        self.vanishing_points = []

    def draw_coordinate_axes(self, vanishing_points, center, scale=100, labels=None, colors=None, flip_z=True,
                             ax=None, return_fig=False):
        """
        Рисует координатные оси X, Y, Z от центра изображения по направлению к точкам схода.

        :param vanishing_points: список [(x1, y1), (x2, y2), (x3, y3)] — координаты VP
        :param center: (cx, cy) — центр изображения (или центр проекции камеры)
        :param scale: длина стрелок (в пикселях)
        :param labels: подписи осей, по умолчанию ['X', 'Y', 'Z']
        :param colors: цвета осей, по умолчанию ['red', 'green', 'blue']
        :param ax: объект matplotlib.axes.Axes. Если не задан — создаётся новый.
        :param return_fig: если True — вернёт (fig, ax), иначе только ax.
        """
        if labels is None:
            labels = ['X', 'Y', 'Z']
        if colors is None:
            colors = ['red', 'green', 'blue']

        created_fig = False
        if ax is None:
            fig, ax = plt.subplots()
            created_fig = True

        cx, cy = center

        for i, (x, y) in enumerate(vanishing_points):
            dx = x - cx
            dy = y - cy
            norm = np.hypot(dx, dy)
            dx_scaled = dx / norm * scale
            dy_scaled = dy / norm * scale

            if flip_z and labels[i].upper() == 'Z':
                dx_scaled *= -1
                dy_scaled *= -1

            # Рисуем стрелку оси
            plt.arrow(cx, cy, dx_scaled, dy_scaled,
                      color=colors[i], width=1.2, head_width=10, length_includes_head=True)

        if return_fig and created_fig:
            return fig, ax
        return ax

    def draw_vp(self, vanishing_points, ax=None, colors=None, labels=None, marker='o', size=60, return_fig=False):
        """
        Рисует точки схода (vanishing points) на графике.

        :param vanishing_points: список [(x1, y1), (x2, y2), (x3, y3)]
        :param ax: matplotlib.axes.Axes — если None, создаётся новый
        :param colors: список цветов ['r', 'g', 'b'] или один цвет
        :param labels: список ['VP1', 'VP2', 'VP3'] — подписи
        :param marker: маркер для точек (по умолчанию 'o')
        :param size: размер маркеров
        :param return_fig: если True — вернёт (fig, ax)
        """
        vanishing_points = np.array(vanishing_points)
        created_fig = False

        if ax is None:
            fig, ax = plt.subplots()
            created_fig = True

        if colors is None:
            colors = ['r', 'g', 'b']
        if labels is None:
            labels = [f'VP{i + 1}' for i in range(len(vanishing_points))]

        for i, (x, y) in enumerate(vanishing_points):
            ax.scatter(x, y, c=colors[i % len(colors)], marker=marker, s=size)
            ax.text(x + 15, y + 15, labels[i], color=colors[i % len(colors)], fontsize=12)

        if return_fig and created_fig:
            return fig, ax
        return ax
