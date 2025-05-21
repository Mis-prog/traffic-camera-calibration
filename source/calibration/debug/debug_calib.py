import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from core import Camera, PointND


def visualize_grid_debug(
        camera: Camera,
        point_start: PointND,
        grid_range: float = 10.0,  # диапазон в метрах от центра
        grid_step: float = 1.0,  # размер клетки
        arrow_len: float = 5.0,  # длина вектора "вверх"
        plane_z: float = 0.0,  # плоскость, на которую кладём сетку
        save_path=None
):
    image = camera.get_image()
    height, width = image.shape[:2]

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_title("Калибровочная сетка (1×1 м) в проекции")
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    plt.imshow(image)

    anchor_3D = camera.project_back(point_start, plane_z=plane_z)
    anchor_x, anchor_y, anchor_z = anchor_3D.get()
    print(anchor_x, anchor_y, anchor_z)

    # Считаем количество узлов в сетке
    count = int(2 * grid_range / grid_step) + 1

    world_points = []
    for i in range(count):
        for j in range(count):
            x = anchor_x - grid_range + i * grid_step
            y = anchor_y - grid_range + j * grid_step
            world_points.append(PointND(np.array([x, y, plane_z])))

    for i in range(count):
        for j in range(count - 1):
            p1 = world_points[i * count + j]
            p2 = world_points[i * count + (j + 1)]
            p1_proj = camera.project_direct(p1).get()
            p2_proj = camera.project_direct(p2).get()
            ax.plot([p1_proj[0], p2_proj[0]], [p1_proj[1], p2_proj[1]], color='blue', linewidth=1)

    for j in range(count):
        for i in range(count - 1):
            p1 = world_points[i * count + j]
            p2 = world_points[(i + 1) * count + j]
            p1_proj = camera.project_direct(p1).get()
            p2_proj = camera.project_direct(p2).get()
            ax.plot([p1_proj[0], p2_proj[0]], [p1_proj[1], p2_proj[1]], color='blue', linewidth=1)

    def draw_arrow_from_3D(p3D):
        base = camera.project_direct(p3D).get()
        tip_point = PointND(p3D.get() + np.array([0, 0, arrow_len]))
        tip = camera.project_direct(tip_point).get()

        # красная точка — основание
        ax.scatter(base[0], base[1], color='red', s=10, zorder=3)

        # чёрная стрелка — вверх
        ax.annotate(
            '', xy=(tip[0], tip[1]), xytext=(base[0], base[1]),
            arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
            annotation_clip=False, label=f'Высота: {arrow_len}'
        )

    top_left = world_points[0]
    top_right = world_points[count - 1]
    bottom_left = world_points[(count - 1) * count]
    bottom_right = world_points[-1]

    for corner in [top_left, top_right, bottom_left, bottom_right]:
        draw_arrow_from_3D(corner)

    arrow_legend = mlines.Line2D([], [], color='black', marker=r'$\uparrow$', linestyle='None',
                                 markersize=10, label=f'Вектор вверх ({arrow_len} м)')
    ax.legend(handles=[arrow_legend])

    plt.savefig(save_path)
    plt.show()


def visualize_coordinate_system(
        camera: Camera,
        save_path
):
    image = camera.get_image()

    scale = 1

    O = PointND([0, 0, 0, 1])
    X = PointND([scale, 0, 0, 1])
    Y = PointND([0, scale, 0, 1])
    Z = PointND([0, 0, scale, 1])

    x = camera.project_direct(X).get()
    y = camera.project_direct(Y).get()
    z = camera.project_direct(Z).get()
