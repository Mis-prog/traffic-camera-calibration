import matplotlib.pyplot as plt
import numpy as np
import cv2


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


def visualize_vps_debug(
        camera,
        step_x=400,
        step_y=300,
        scale=100,
        save_path=None,
        show=False,
        flip_z=True,
        dpi=200
):
    """
    Визуализирует координатные оси на изображении камеры по точкам схода.

    :param camera: объект камеры с методом get_image(), intrinsics.get(), extrinsics.get_rotation()
    :param step_x: шаг сетки по оси X (в пикселях)
    :param step_y: шаг сетки по оси Y (в пикселях)
    :param scale: длина координатных стрелок
    :param save_path: путь для сохранения изображения
    :param show: показывать ли окно с результатом
    :param flip_z: отражать ли ось Z
    :param dpi: разрешение сохранённого изображения
    """
    image = camera.get_image()

    K = camera.intrinsics.get()
    R = camera.extrinsics.get_rotation()

    # Восстановим точки схода из R и K
    vp1 = K @ R[:, 0]
    vp2 = K @ R[:, 1]
    vp3 = K @ R[:, 2]

    vp1 = vp1[:2] / vp1[2]
    vp2 = vp2[:2] / vp2[2]
    vp3 = vp3[:2] / vp3[2]

    vps = np.array([vp1, vp2, vp3])

    h, w = image.shape[:2]
    centers = [
        (int(x), int(y))
        for y in np.arange(step_y, h, step_y)
        for x in np.arange(step_x, w, step_x)
    ]

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.imshow(image)

    for center in centers:
        draw_coordinate_axes_from_vps(
            vanishing_points=vps,
            center=center,
            scale=scale,
            flip_z=flip_z,
            ax=ax
        )

    ax.set_title("Vanishing Point Coordinate Axes")
    ax.axis('off')
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
        print(f"[DEBUG] Saved visualization to {save_path}")

    if show:
        plt.show()
    else:
        plt.close(fig)
