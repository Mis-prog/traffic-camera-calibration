import numpy as np
import cv2


def compute_distorted_r(r_vals, k1):
    r2 = r_vals ** 2
    L = 1 / (1 + k1 * r2)
    return L * r_vals


from scipy.interpolate import interp1d


def build_inverse_vector(k1, r_max, num_samples=10000):
    r_vals = np.linspace(0, r_max, num_samples)
    r_distorted = compute_distorted_r(r_vals, k1)
    mask = r_vals > 0
    scale = np.max(r_distorted[mask] / r_vals[mask])

    r_distorted, indices = np.unique(r_distorted, return_index=True)
    r_vals = r_vals[indices]
    inverse_func = interp1d(r_distorted, r_vals, bounds_error=False, fill_value="extrapolate")

    print(f'scale {scale}')

    return inverse_func, scale  # функция: r_hat → r


def build_undistort_map(img_shape, k1, cx, cy, inverse_func):
    h, w = img_shape[:2]
    map_x = np.zeros((h, w), dtype=np.float32)
    map_y = np.zeros((h, w), dtype=np.float32)

    for j in range(h):
        for i in range(w):
            dx = i - cx
            dy = j - cy
            r_hat = np.sqrt(dx ** 2 + dy ** 2)
            if r_hat == 0:
                map_x[j, i] = i
                map_y[j, i] = j
                continue

            r = inverse_func(r_hat)
            scale = r / r_hat
            x = cx + dx * scale
            y = cy + dy * scale

            map_x[j, i] = x
            map_y[j, i] = y

    return map_x, map_y


def build_undistort_map_vec(img_shape, k1, cx, cy, inverse_func, scale=1.0):
    h, w = img_shape[:2]

    # Сетка координат
    x, y = np.meshgrid(np.arange(w), np.arange(h))
    dx = (x - cx) * scale
    dy = (y - cy) * scale
    r_hat = np.sqrt(dx ** 2 + dy ** 2)

    # Обратное преобразование r_hat → r
    r = inverse_func(r_hat.ravel()).reshape(r_hat.shape)
    scale = np.ones_like(r_hat)
    valid = r_hat > 0
    scale[valid] = r[valid] / r_hat[valid]

    map_x = (cx + dx * scale).astype(np.float32)
    map_y = (cy + dy * scale).astype(np.float32)

    return map_x, map_y


def undistort_image(img, k1):
    h, w = img.shape[:2]
    cx, cy = w / 2, h / 2
    r_max = np.sqrt(cx ** 2 + cy ** 2)

    inverse_func, scale = build_inverse_vector(k1, r_max)
    # map_x, map_y = build_undistort_map(img.shape, k1, k2, cx, cy, inverse_func)
    map_x, map_y = build_undistort_map_vec(img.shape, k1, cx, cy, inverse_func, scale=scale)

    print("min/max map_x:", np.min(map_x), np.max(map_x))
    print("min/max map_y:", np.min(map_y), np.max(map_y))

    undistorted = cv2.remap(img, map_x, map_y, interpolation=cv2.INTER_LINEAR)
    return undistorted


img = cv2.imread("crossroads.jpg")
k1 = -2.3593577448399698513e-07
result = undistort_image(img, k1)
cv2.imwrite("undistorted_output_one.jpg", result)
