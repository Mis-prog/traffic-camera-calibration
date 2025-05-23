import matplotlib.pyplot as plt
import matplotlib.cm as cm
import hashlib


def visualize_source(data: dict, image=None):
    """
    data: {
        "group1": [ [(x1,y1), (x2,y2)], ... ],
        "group2": [ [(x1,y1), (x2,y2)], ... ],
    }
    image: optional background image (e.g. from camera.get_image())
    """
    fig, ax = plt.subplots()

    if image is not None:
        ax.imshow(image)

    for key, lines in data.items():
        color = get_color_by_key(key)

        for i, (p1, p2) in enumerate(lines):
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, linewidth=2)
            ax.scatter(*p1, color=color, s=10)
            ax.scatter(*p2, color=color, s=10)

        # добавим линию в легенду один раз
        ax.plot([], [], color=color, label=key)

    ax.legend(loc='upper right')
    ax.axis('equal')
    plt.tight_layout()
    plt.show()


def get_color_by_key(key):
    """Уникальный цвет по имени группы"""
    cmap = cm.get_cmap('tab10')
    hash_val = int(hashlib.md5(key.encode()).hexdigest(), 16)
    return cmap(hash_val % 10)