import cv2
import numpy as np

scale = 0.5
point_radius = 5
point_thickness = -1  # -1 = заливка

curves = []
current_curve = []

selected_point = None  # (curve_index, point_index)
dragging = False

def find_nearest_point(x, y, threshold=10):
    """Поиск ближайшей точки в масштабе экрана"""
    for ci, curve in enumerate(curves + [current_curve]):
        for pi, (px, py) in enumerate(curve):
            dx = int(px * scale) - x
            dy = int(py * scale) - y
            if dx * dx + dy * dy <= threshold ** 2:
                return (ci, pi)
    return None

def mouse_callback(event, x, y, flags, param):
    global current_curve, curves, selected_point, dragging

    x_orig = int(x / scale)
    y_orig = int(y / scale)

    if event == cv2.EVENT_LBUTTONDOWN:
        nearest = find_nearest_point(x, y)
        if nearest:
            selected_point = nearest
            dragging = True
        else:
            current_curve.append((x_orig, y_orig))

    elif event == cv2.EVENT_MOUSEMOVE and dragging and selected_point:
        ci, pi = selected_point
        if ci < len(curves):
            curves[ci][pi] = (x_orig, y_orig)
        else:
            current_curve[pi] = (x_orig, y_orig)

    elif event == cv2.EVENT_LBUTTONUP:
        dragging = False
        selected_point = None

    elif event == cv2.EVENT_RBUTTONDOWN:
        nearest = find_nearest_point(x, y)
        if nearest:
            ci, pi = nearest
            if ci < len(curves):
                del curves[ci][pi]
                if len(curves[ci]) == 0:
                    del curves[ci]
            else:
                del current_curve[pi]

        elif current_curve:
            curves.append(current_curve.copy())
            current_curve.clear()

# Загрузка изображения
image_orig = cv2.imread("../../example/pushkin_aksakov/image/crossroads.jpg")
if image_orig is None:
    raise FileNotFoundError("Изображение не найдено")

h, w = image_orig.shape[:2]
image_scaled = cv2.resize(image_orig, (int(w * scale), int(h * scale)))

cv2.namedWindow("Click to draw")
cv2.setMouseCallback("Click to draw", mouse_callback)

while True:
    display = image_scaled.copy()

    def draw_curve(curve, color_line, color_points):
        for i in range(1, len(curve)):
            pt1 = tuple(int(v * scale) for v in curve[i - 1])
            pt2 = tuple(int(v * scale) for v in curve[i])
            cv2.line(display, pt1, pt2, color_line, 2)
        for pt in curve:
            center = tuple(int(v * scale) for v in pt)
            cv2.circle(display, center, point_radius, color_points, point_thickness)

    # Завершённые кривые (зелёные)
    for curve in curves:
        draw_curve(curve, (0, 255, 0), (0, 200, 0))

    # Текущая кривая (красная)
    draw_curve(current_curve, (0, 0, 255), (0, 0, 200))

    cv2.imshow("Click to draw", display)
    key = cv2.waitKey(20)

    if key == 27:
        break
    elif key == ord("s"):
        np.save("clicked_curves.npy", np.array(curves, dtype=object))
        print("Сохранено в 'clicked_curves.npy'")
    elif key == ord("c"):
        curves.clear()
        current_curve.clear()
        print("Очищено")

cv2.destroyAllWindows()
