import cv2
import numpy as np

pts_src = np.array([[382,444], [106, 307], [171, 127], [451, 217]]) # спутник
pts_dst = np.array([[300, 518], [560, 182], [927, 266], [818, 687]]) # камера

h_inv, status = cv2.findHomography(pts_dst, pts_src)
print(h_inv)

# Проверяем обратное преобразование
pts_dst_homogeneous = np.hstack([690, 360,1])  # Добавляем координату 1 для гомогенной системы
pts_transformed = (h_inv @ pts_dst_homogeneous.T).T  # Применяем матрицу гомографии
pts_transformed /= pts_transformed[:, 2][:, np.newaxis]  # Нормируем по третьей координате

# Выводим результаты
print("Исходные точки (камера):")
print(pts_dst)

print("Преобразованные точки (должны совпадать с исходными спутника):")
print(pts_transformed[:, :2])

print("Оригинальные точки спутника:")
print(pts_src)
