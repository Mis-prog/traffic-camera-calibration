import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from scipy.spatial.transform import Rotation

from source.camera_model import Camera
from source.pointND import PointND
from source.new_optimization import NewOptimization,RESIDUALS
from source.data_preparation import fun_lines, load_params, load_data


def init(h):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.zaxis.line.set_color((1.0, 1.0, 1.0, 0.0))  # Ось Z
    ax.xaxis.line.set_color((1.0, 1.0, 1.0, 0.0))  # Ось X
    ax.yaxis.line.set_color((1.0, 1.0, 1.0, 0.0))  # Ось Y

    ax.xaxis.set_tick_params(labelleft=False, labelbottom=False)  # Убираем метки для оси X
    ax.yaxis.set_tick_params(labelleft=False, labelbottom=False)  # Убираем метки для оси Y
    ax.zaxis.set_tick_params(labelleft=False, labelbottom=False)  # Убираем метки для оси Z

    ax.xaxis.set_ticks_position('none')  # Убираем засечки для оси X
    ax.yaxis.set_ticks_position('none')  # Убираем засечки для оси Y
    ax.zaxis.set_ticks_position('none')  # Убираем засечки для оси Z

    # Настройка углов обзора
    ax.view_init(elev=20, azim=30)

    ax.set_proj_type('persp')

    ax.set_zlim(0, h + 10)
    ax.set_xlim(-40, 40)
    ax.set_ylim(-40, 40)

    return ax


def plot_axies(position, angles=[]):
    if not angles:
        ax.quiver(*position, 15, 0, 0, color='black')
        ax.quiver(*position, 0, 15, 0, color='black')
        ax.quiver(*position, 0, 0, 15, color='black')
        ax.scatter(0, 0, 0, marker='^', s=100, color='red', label='Мировая система координат')
        text_size = 12
        ax.text(position[0] + 15, position[1] + 1, position[2], 'X', color='black', fontsize=text_size)
        ax.text(position[0], position[1] + 15, position[2], 'Y', color='black', fontsize=text_size)
        ax.text(position[0], position[1], position[2] + 15, 'Z', color='black', fontsize=text_size)
    else:
        rot = Rotation.from_euler('zxy', angles, degrees=True).as_matrix()
        transform = np.eye(4)
        transform[:3, :3] = rot
        transform[:3, 3] = -rot @ position
        x_position = transform @ np.array([15, 0, 0, 1])
        y_position = transform @ np.array([0, 15, 0, 1])
        z_position = transform @ np.array([0, 0, 15, 1])
        origin = transform @ np.array([0, 0, 0, 1])
        # print(f'Положение камеры:\nx: {x_position[:-1]}\ny: {y_position[:-1]}\nz: {z_position[:-1]}')
        distances = np.linalg.norm(transform[:3, 3])

        ax.scatter(*transform[:3, 3], color='red', label='Система координат камеры камеры')
        # label=f'{np.around(transform[:3, 3], 2)}, расстонияние до центра {round(distances, 2)}')
        ax.quiver(*origin[:-1], *(x_position[:-1] - origin[:-1]), color='black')
        ax.quiver(*origin[:-1], *(y_position[:-1] - origin[:-1]), color='black')
        ax.quiver(*origin[:-1], *(z_position[:-1] - origin[:-1]), color='black')
        text_size = 12
        ax.text(*x_position[:-1], 'X', color='black', fontsize=text_size)
        ax.text(*y_position[:-1], 'Y', color='black', fontsize=text_size)
        ax.text(*z_position[:-1], 'Z', color='black', fontsize=text_size)

        ax.legend(loc='upper center')


def get_normals(x, y, length=4):
    """
    Строит нормальные (перпендикулярные) отрезки длиной `length` для заданных точек линии `x, y`.

    Возвращает:
    - norm_lines_x: список массивов x-координат отрезков
    - norm_lines_y: список массивов y-координат отрезков
    """
    norm_lines_x = []
    norm_lines_y = []

    # Выбираем точки для построения нормалей
    indices = [73, 69]  # Можно выбрать другие индексы
    for idx in indices:
        if idx >= len(x) - 1:  # Проверяем границы массива
            continue

        # Определяем направление линии в данной точке
        dx = x[idx + 1] - x[idx]
        dy = y[idx + 1] - y[idx]

        # Вычисляем нормальный вектор
        norm = np.array([-dy, dx])
        norm = length * norm / np.linalg.norm(norm)  # Делаем его длиной `length`

        # Вычисляем координаты концов нормального отрезка
        norm_x = [x[idx] - norm[0] / 2, x[idx] + norm[0] / 2]
        norm_y = [y[idx] - norm[1] / 2, y[idx] + norm[1] / 2]

        norm_lines_x.append(norm_x)
        norm_lines_y.append(norm_y)

    return norm_lines_x, norm_lines_y


# эталонные значения
camera = Camera()
camera.load_scene('../pushkin_aksakov/image/image.webp')
params = load_params('../pushkin_aksakov/marked_data/calib_data.txt')
camera.set_params(params)

ax = init(params[-1])
plot_axies([0, 0, 0])
plot_axies([0, 0, params[-1]], params[1:4])

data = {}
data['parallel-1'] = []
data['parallel-2'] = []
data['angle'] = []
data['point_to_point'] = []

# Паралельные линии
start, end = load_data('../pushkin_aksakov/marked_data/parallel_lines_1.txt')[1]
start3d = camera.back_crop(start)
end3d = camera.back_crop(end)
print(np.linalg.norm(end3d.get() - start3d.get()))

for y_dist in [-10, 0, 10]:
    x = np.linspace(-60, 25, 100)
    y = fun_lines(x, start3d, end3d) - y_dist
    points = [camera.direct_crop(PointND([xi, yi])) for xi, yi in zip(x, y)]
    x_new, y_new = zip(*[p.get() for p in points])
    data['parallel-1'].append(np.array([x_new, y_new]))
    plt.plot(x, y, color='black')

norm_x, norm_y = get_normals(x, y, length=4)
for i in range(len(norm_x)):
    plt.plot(norm_x[i], norm_y[i], color='black', label=f"Normal {i + 1}")
    points = [camera.direct_crop(PointND([xi, yi])) for xi, yi in zip(norm_x[i], norm_y[i])]
    x_new, y_new = zip(*[p.get() for p in points])
    data['point_to_point'].append(np.array([x_new, y_new]))

# Ортогональные линии
x = np.linspace(5, 13, 100)
y = fun_lines(x, start3d, end3d, orthogonal=True)
plt.plot(x, y, color='black')
points = [camera.direct_crop(PointND([xi, yi])) for xi, yi in zip(x, y)]
x_new, y_new = zip(*[p.get() for p in points])
data['angle'].append(np.array([x_new, y_new]))

start, end = load_data('../pushkin_aksakov/marked_data/parallel_lines_2.txt')[1]
start3d = camera.back_crop(start)
end3d = camera.back_crop(end)
print(np.linalg.norm(end3d.get() - start3d.get()))
for y_dist in [-10, 0, 10]:
    x = np.linspace(-17, 17, 100)
    y = fun_lines(x, start3d, end3d) - y_dist
    points = [camera.direct_crop(PointND([xi, yi])) for xi, yi in zip(x, y)]
    x_new, y_new = zip(*[p.get() for p in points])
    data['parallel-2'].append(np.array([x_new, y_new]))
    plt.plot(x, y, color='black')

# Ортогональные линии
x = np.linspace(0, 4, 100)
y = fun_lines(x, start3d, end3d, orthogonal=True)
plt.plot(x, y, color='black')
points = [camera.direct_crop(PointND([xi, yi])) for xi, yi in zip(x, y)]
x_new, y_new = zip(*[p.get() for p in points])
data['angle'].append(np.array([x_new, y_new]))

plt.show()

data_optimize = {}

data_optimize['parallel-1'] = []
data_optimize['parallel-2'] = []
data_optimize['angle'] = []
data_optimize['point_to_point'] = []

for x, y in data['parallel-1']:
    plt.plot(x, y, color='black')
    data_optimize['parallel-1'].append([PointND([x[0], y[0]]), PointND([x[-1], y[-1]])])

for x, y in data['parallel-2']:
    plt.plot(x, y, color='black')
    data_optimize['parallel-2'].append([PointND([x[0], y[0]]), PointND([x[-1], y[-1]])])

for x, y in data['angle']:
    plt.plot(x, y, color='black')
    data_optimize['angle'].append([PointND([x[0], y[0]]), PointND([x[-1], y[-1]])])

for x, y in data['point_to_point']:
    plt.plot(x, y, color='black')
    data_optimize['point_to_point'].append([PointND([x[0], y[0]]), PointND([x[-1], y[-1]])])


plt.xlim(0, 1920)
plt.ylim(0, 1080)
plt.gca().invert_yaxis()
plt.show()

curr = []
for i in range(1, len(data_optimize['parallel-1'])):
    curr.append(data_optimize['parallel-1'][i - 1] + data_optimize['parallel-1'][i])
data_optimize['parallel-1'] = np.array(curr)

curr = []
for i in range(1, len(data_optimize['parallel-2'])):
    curr.append(data_optimize['parallel-2'][i - 1] + data_optimize['parallel-2'][i])
data_optimize['parallel-2'] = np.array(curr)
data_optimize['angle'] = np.array
data_optimize['point_to_point'] = np.array(data_optimize['point_to_point'])
optimize = NewOptimization(camera)
optimize.back_projection(data_optimize)

HIST = [np.sum(values) for values in RESIDUALS]


plt.title('График погрешности')
plt.ylabel('Точность')
plt.xlabel('Количество итераций')
plt.plot(np.arange(0, len(HIST)), HIST)
plt.show()
