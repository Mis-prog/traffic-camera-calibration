import numpy as np
import cv2
import matplotlib.pyplot as plt
from .debug_vp import draw_coordinate_axes_from_vps


def visualize_vanishing_point_debug(
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
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

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
    ax.imshow(image_rgb)

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
