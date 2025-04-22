import numpy as np


def normalize_points(points):
    mean = np.mean(points, axis=0)
    std = np.std(points, axis=0)
    return (points - mean) / std, mean, std


def denormalize_points(points, mean, std):
    return points * std + mean


def compute_transformation_matrix(image_points, gps_points):
    # Нормализация точек
    image_points, image_mean, image_std = normalize_points(image_points)
    gps_points, gps_mean, gps_std = normalize_points(gps_points)

    num_points = image_points.shape[0]

    A = []
    B = []

    for i in range(num_points):
        x, y = image_points[i]
        x_gps, y_gps = gps_points[i]

        # Линейная модель
        A.append([x, y, 1, 0, 0, 0])
        A.append([0, 0, 0, x, y, 1])
        B.append(x_gps)
        B.append(y_gps)

    A = np.array(A)
    B = np.array(B)

    # Решение системы уравнений Ax = B
    x, _, _, _ = np.linalg.lstsq(A, B, rcond=None)

    # Формирование матрицы преобразования
    transformation_matrix = np.array([
        [x[0], x[1], x[2]],
        [x[3], x[4], x[5]],
        [0, 0, 1]
    ])

    return transformation_matrix, image_mean, image_std, gps_mean, gps_std


def getRealcoords(pt, transformation_matrix, image_mean, image_std, gps_mean, gps_std):
    pt_normalized = (pt - image_mean) / image_std
    vector = np.array([pt_normalized[0], pt_normalized[1], 1], dtype=np.float64)

    result = np.dot(transformation_matrix, vector)
    result = result / result[-1]  # Нормализация гомогенной координаты
    result = denormalize_points(result[:2], gps_mean, gps_std)

    return result.astype(np.float64)


def evaluate_transformation_matrix(image_points, gps_points, transformation_matrix, image_mean, image_std, gps_mean,
                                   gps_std):
    transformed_points = np.array(
        [getRealcoords(pt, transformation_matrix, image_mean, image_std, gps_mean, gps_std) for pt in image_points])
    errors = np.linalg.norm(transformed_points - gps_points, axis=1)
    rmse = np.sqrt(np.mean(errors ** 2))
    return rmse


# Пример использования
image_points = np.array([[554, 237], [451, 348], [343, 490], [603, 593],  [934, 693], [962, 438], [978, 284],[887, 220], [650, 203]])
gps_points = np.array([[54.725249081667606, 55.94052135944367], [54.725227396080314, 55.9406340122223], [54.725199514593825, 55.94080567359925], [54.72530174661709, 55.94085395336152],
                       [54.725410174238775, 55.940907597541816], [54.725441153505955, 55.94073057174683],[54.72545974105493, 55.94063937664033],[54.72543185972829,55.94049453735352]
                       ,[54.72531104042461,55.940467715263374]])

# Вычисление матрицы преобразования
transformation_matrix, image_mean, image_std, gps_mean, gps_std = compute_transformation_matrix(image_points,
                                                                                                gps_points)

# Оценка качества матрицы
rmse = evaluate_transformation_matrix(image_points, gps_points, transformation_matrix, image_mean, image_std, gps_mean,
                                      gps_std)
print("Transformation Matrix:")
print(transformation_matrix)
print("Root Mean Squared Error (RMSE):", rmse)

# Преобразование новой точки
new_point = (869, 511)
transformed_point = getRealcoords(new_point, transformation_matrix, image_mean, image_std, gps_mean, gps_std)
print("Transformed Point:", transformed_point)
