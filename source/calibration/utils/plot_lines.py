import cv2
import matplotlib.pyplot as plt
from .data_preparation import load_lines


def draw_lines_on_image(image_path, lines, line_color=(0, 0, 255), thickness=2):
    """
    Загружает изображение и отрисовывает на нём заданные линии.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Изображение не найдено: {image_path}")
    for pt1, pt2 in lines:
        cv2.line(image, pt1, pt2, line_color, thickness)
    return image


if __name__ == "__main__":
    lines = load_lines('marked/horizontal_lines_all.json')
    image_with_lines = draw_lines_on_image('image/pattern_corrected_image.png', lines)
    plt.imshow(cv2.cvtColor(image_with_lines, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.title("Линии, наложенные на изображение")
    plt.show()
