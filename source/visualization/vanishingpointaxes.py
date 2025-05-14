import numpy as np
import matplotlib.pyplot as plt
from .drawable import Drawable

class VanishingPointAxes(Drawable):
    def __init__(self, vanishing_points=None, center=(960, 540), scale=100):
        self.vanishing_points = vanishing_points or []
        self.center = center
        self.scale = scale

    def draw(self, ax):
        self._draw_vp(ax)
        self._draw_coordinate_axes(ax)

    def _draw_coordinate_axes(self, ax, labels=None, colors=None, flip_z=True):
        labels = labels or ['X', 'Y', 'Z']
        colors = colors or ['red', 'green', 'blue']

        cx, cy = self.center

        for i, (x, y) in enumerate(self.vanishing_points):
            dx = x - cx
            dy = y - cy
            norm = np.hypot(dx, dy)
            dx_scaled = dx / norm * self.scale
            dy_scaled = dy / norm * self.scale

            if flip_z and labels[i].upper() == 'Z':
                dx_scaled *= -1
                dy_scaled *= -1

            ax.arrow(cx, cy, dx_scaled, dy_scaled,
                     color=colors[i], width=1.2, head_width=10, length_includes_head=True)
            ax.text(cx + dx_scaled, cy + dy_scaled, labels[i], color=colors[i], fontsize=12)

    def _draw_vp(self, ax, colors=None, labels=None, marker='o', size=60):
        colors = colors or ['r', 'g', 'b']
        labels = labels or [f'VP{i + 1}' for i in range(len(self.vanishing_points))]

        for i, (x, y) in enumerate(self.vanishing_points):
            ax.scatter(x, y, c=colors[i % len(colors)], marker=marker, s=size)
            ax.text(x + 15, y + 15, labels[i], color=colors[i % len(colors)], fontsize=12)