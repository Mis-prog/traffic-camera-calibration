import matplotlib.pyplot as plt
import numpy as np


def draw_coordinate_axes_from_vps(
        vanishing_points,
        center,
        scale=100,
        labels=None,
        colors=None,
        flip_z=True,
        image=None,
        save_path=None,
        ax=None
):
    if labels is None:
        labels = ['X', 'Y', 'Z']
    if colors is None:
        colors = ['red', 'green', 'blue']

    cx, cy = center

    # Подготовка осей
    if ax is None:
        fig, ax = plt.subplots()

    # Отображаем фоновое изображение
    if image is not None:
        ax.imshow(image)

    # Рисуем координатные оси
    for i, (x, y) in enumerate(vanishing_points):
        dx = x - cx
        dy = y - cy
        norm = np.hypot(dx, dy)
        dx_scaled = dx / norm * scale
        dy_scaled = dy / norm * scale

        if flip_z and labels[i].upper() == 'Z':
            dx_scaled *= -1
            dy_scaled *= -1

        ax.arrow(cx, cy, dx_scaled, dy_scaled,
                 color=colors[i], width=1.2, head_width=10, length_includes_head=True)
        ax.text(cx + dx_scaled * 1.1, cy + dy_scaled * 1.1,
                labels[i], fontsize=12, color=colors[i], weight='bold')

    ax.set_title("Coordinate Axes from Vanishing Points")
    ax.axis('off')

    if save_path:
        plt.savefig(save_path, dpi=150)
