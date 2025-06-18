import numpy as np
import matplotlib.pyplot as plt

from core import Camera, PointND
from calibration.utils import gps_to_enu


def projection_line(camera, data, lat0, lon0, save_path, R=np.array([[1, 0], [0, 1]])):
    image = camera.get_image()
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.imshow(image)

    annotation_plotted = False
    projected_plotted = False

    for line in data:
        p1, p2 = line['pixel']
        P1_gps, P2_gps = line['gps']
        P1, P2 = [
            camera.project_direct(PointND([*R @ gps_to_enu(*point, lat0, lon0), 0])).get()
            for point in line['gps']
        ]

        # Один раз добавим label
        label_ann = 'Исходные линии' if not annotation_plotted else None
        label_proj = 'Спроецированные линии' if not projected_plotted else None

        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'r-', label=label_ann)
        ax.plot([P1[0], P2[0]], [P1[1], P2[1]], 'b--', label=label_proj)

        ax.plot(*p1, 'ro')
        ax.plot(*p2, 'ro')
        ax.plot(*P1, 'bo')
        ax.plot(*P2, 'bo')

        annotation_plotted = True
        projected_plotted = True

    ax.set_title("Сравнение аннотаций и проекций")
    ax.legend(loc='lower right')
    ax.axis('off')

    fig.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
