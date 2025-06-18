import cv2
import numpy as np

img = cv2.imread("../../example/prospect/data/pattern_corrected_image.png", cv2.IMREAD_GRAYSCALE)

lsd = cv2.createLineSegmentDetector()

x1, y1, x2, y2 = 100, 600, 1000, 1000  # координаты ROI
roi_mask = np.zeros_like(img, dtype=np.uint8)
roi_mask[y1:y2, x1:x2] = 255

masked_img = cv2.bitwise_and(img, img, mask=roi_mask)
lines, _, _, _ = lsd.detect(masked_img)


drawn_img = lsd.drawSegments(img.copy(), lines)

scale = 0.5  # уменьшить в 2 раза
drawn_img = cv2.resize(drawn_img, (0, 0), fx=scale, fy=scale)

cv2.imshow("Detected Lines", drawn_img)
cv2.waitKey(0)
cv2.destroyAllWindows()

from lu_vp_detect import VPDetection
import cv2
import matplotlib.pyplot as plt
import numpy as np


def draw_coordinate_axes_from_vps(vanishing_points, center, scale=100, labels=None, colors=None, flip_z=True):
    """
    Рисует координатные оси X, Y, Z от центра изображения по направлению к точкам схода.

    :param vanishing_points: список [(x1, y1), (x2, y2), (x3, y3)] — координаты VP
    :param center: (cx, cy) — центр изображения (или центр проекции камеры)
    :param scale: длина стрелок (в пикселях)
    :param labels: подписи осей, по умолчанию ['X', 'Y', 'Z']
    :param colors: цвета осей, по умолчанию ['red', 'green', 'blue']
    """
    if labels is None:
        labels = ['X', 'Y', 'Z']
    if colors is None:
        colors = ['red', 'green', 'blue']

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


length_thresh = 20
principal_point = None
focal_length = 1419.59
seed = 1000

img = '../../example/prospect/data/pattern_corrected_image.png'
# img = '../example/karls_marks/image/scene_from_crossroads_not_dist.png'
# img = '../example/karls_marks/screenshot_1746977335965.jpg'
image = cv2.imread(img)
# image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# plt.imshow(image_rgb)

vpd = VPDetection(length_thresh, principal_point, focal_length, seed)
vps = vpd.find_vps(img)
print(vps)
VP_pixel = vpd.vps_2D
print(VP_pixel)

image_width = 1920
image_height = 1080
center = (image_width // 2 - 150, image_height // 2 + 270)
draw_coordinate_axes_from_vps(VP_pixel, center)

vpd.create_debug_VP_image(save_image='debug.png')

plt.scatter(VP_pixel[:, 0], VP_pixel[:, 1], label='VP Detect')
#
# for x, y in VP_pixel:
#     plt.scatter(x, y)


from core.camera_model import Camera

camera = Camera('../../example/pushkin_aksakov/image/pattern_corrected_image.png')
camera.set_params([1419.59, -142.56, 49.5, -185.62, -12.82, -18.38, 30.63])

K = camera.get_K()
print(f'Matrix intrinsics:\n{K}')
R = camera.get_R()
print(f'Matrix rot:\n{R}')
print(f'Matrix M:\n{K @ R}')

C = np.array([[-12.82], [-18.38], [30.63]])  # столбец, чтобы собрать [R | t]
t = -R @ C  # вектор переноса (перевод центра камеры в систему камеры)
Rt = np.hstack((R, t))  # 3x4 матрица [R | t]
P = K @ Rt
VP1 = K @ R[:, 0]
VP1_pixel = [VP1[0] / VP1[2], VP1[1] / VP1[2]]

VP2 = K @ R[:, 1]
VP2_pixel = [VP2[0] / VP2[2], VP2[1] / VP2[2]]

V3_calc = np.dot(VP1, VP2)
VP3 = K @ R[:, 2]
VP3_pixel = [VP3[0] / VP3[2], VP3[1] / VP3[2]]

VP_opt = np.array([VP1_pixel, VP2_pixel, VP3_pixel])

plt.scatter(VP_opt[:, 0], VP_opt[:, 1], label='VP Matrix Camera')
draw_coordinate_axes_from_vps(VP_opt, center, scale=150)
plt.legend()
plt.show()
