import matplotlib.pyplot as plt
import numpy as np

from main import *


# Столбы
def method_pole(count=5, plot=False, error=0):
    global obj, pole_data, data
    pole = [obj for obj in scene_objects if obj['type'] == 'pole'][::count]
    pole_data = []
    pole_data_vp = []
    label_added = False  # <--- флаг, чтобы метка добавилась один раз

    for obj in pole:
        p1_3d, p2_3d = obj['geometry']
        if error == 0:
            p1_2d = camera.project_direct(PointND(p1_3d, add_weight=True)).get()
            p2_2d = camera.project_direct(PointND(p2_3d, add_weight=True)).get()

        else:
            p1_2d = camera.project_direct(PointND(p1_3d, add_weight=True)).get() + np.random.randint(-error, error,
                                                                                                     size=2)
            p2_2d = camera.project_direct(PointND(p2_3d, add_weight=True)).get() + np.random.randint(-error, error,
                                                                                                     size=2)

        pole_data_vp.append([p1_2d, p2_2d])

        data = {"pixel": p1_2d, "gps": p1_3d}

        if plot:
            if not label_added:
                ax.scatter(*p1_2d, c='b', label='Ошибка проекции точек')
                label_added = True
            else:
                ax.scatter(*p1_2d, c='b')

        pole_data.append(data)
    return pole_data, pole_data_vp


def method_crosswalk(count=5, plot=False, error=0):
    crosswalks = [obj for obj in scene_objects if obj['type'] == 'crosswalk'][::count]
    crosswalk_dataset = []
    label_added = False  # <--- флаг, чтобы метка добавилась один раз
    for obj in crosswalks:
        p1, p2, p3, p4 = obj['geometry']
        if np.linalg.norm(np.array(p1) - np.array(p4)) == 4:
            if error == 0:
                p1 = camera.project_direct(PointND(p1, add_weight=True)).get()
                p4 = camera.project_direct(PointND(p4, add_weight=True)).get()
            else:
                p1 = camera.project_direct(PointND(p1, add_weight=True)).get() + np.random.randint(-error, error,
                                                                                                   size=2)
                p4 = camera.project_direct(PointND(p4, add_weight=True)).get() + np.random.randint(-error, error,
                                                                                                   size=2)

            if plot:
                if not label_added:
                    ax.plot([p1[0], p4[0]], [p1[1], p4[1]], color='red', linewidth=2, label="Ошибка длины отрезков")
                    label_added = True
                else:
                    ax.plot([p1[0], p4[0]], [p1[1], p4[1]], color='red', linewidth=2)

            crosswalk_dataset.append([p1, p4])
        elif np.linalg.norm(np.array(p1) - np.array(p2)) == 4:
            if error == 0:
                p1 = camera.project_direct(PointND(p1, add_weight=True)).get()
                p2 = camera.project_direct(PointND(p2, add_weight=True)).get()
            else:
                p1 = camera.project_direct(PointND(p1, add_weight=True)).get() + np.random.randint(-error, error,
                                                                                                   size=2)
                p2 = camera.project_direct(PointND(p2, add_weight=True)).get() + np.random.randint(-error, error,
                                                                                                   size=2)

            if plot:
                if not label_added:
                    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='red', linewidth=2)
                    label_added = True
                else:
                    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='red', linewidth=2)

            crosswalk_dataset.append([p1, p2])

    return crosswalk_dataset


def method_interline_distance(plot=False, error=0):
    interline_distance = []
    label_added = False  # <--- флаг, чтобы метка добавилась один раз
    for p1, p2 in full_lane_x:
        if error == 0:
            p1 = camera.project_direct(PointND(p1, add_weight=True)).get()
            p2 = camera.project_direct(PointND(p2, add_weight=True)).get()
        else:
            p1 = camera.project_direct(PointND(p1, add_weight=True)).get() + np.random.randint(-error, error,
                                                                                               size=2)
            p2 = camera.project_direct(PointND(p2, add_weight=True)).get() + np.random.randint(-error, error,
                                                                                               size=2)

        interline_distance.append([p1, p2])
        if plot:
            if not label_added:
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='lime', linewidth=2,
                        label='Ошибка межлинейного расстояния')
                label_added = True
            else:
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='lime', linewidth=2)

    return interline_distance


pole, pole_vp = method_pole(count=3, plot=False, error=5)
interline_distance = method_interline_distance(plot=False, error=5)

vp1_manual = VanishingPointEstimatorManual().estimate(interline_distance)
vp3_manual = VanishingPointEstimatorManual().estimate(pole_vp)
print(f'Точки схода: {vp1_manual, vp3_manual}')

camera_test = Camera(size=(1080, 1920))
vp_init = VanishingPointCalibration(camera_test)
vp_init.set_vanishing_points(vpX=vp1_manual, vpZ=vp3_manual)
vp_init.run(None)

pole, pole_vp = method_pole(count=3, plot=True, error=10)
crosswalks = method_crosswalk(count=6, plot=True, error=10)
interline_distance = method_interline_distance(plot=True, error=10)

DATA = []

data = {
    "point_to_point": pole,
    "line_length": crosswalks,
    "interline_distance": interline_distance
}

# # Первая компонента
# residualds_blocs = [
#     lambda cam, data: (
#         np.array(residual_reprojection_point(cam, data, group='point_to_point')) * (1 / 100),
#         'Ошибка проекции точек'
#     ),
#     # lambda cam, data: (np.array(residual_line_length(cam, data, group='line_length', expected=4)) * (1),
#     #                    'Ошибка длины отрезков'),
#     # lambda cam, data: (
#     #     np.array(residual_interline_distance(cam, data, group='interline_distance', expected=4)) * (1),
#     #     'Ошибка межлинейного расстояния')
# ]
#
# camera_test.set_params_from_list([1065.05, -145.46, 60.81, 175.58, 0.0, 0.0, 15.0])
#
# refine = RefineOptimizer(
#     camera=camera_test,
#     residual_blocks=residualds_blocs,
#     mask=[0, 1, 2, 3, 6],
#     bounds=[[500, -360, -360, -360, 15],
#             [1500, 360, 360, 360, 40]],
#     method='trf'
# )
#
# refine.run(data=data)
# print("Delta 1", - np.array(camera_test.get_params()) + np.array(camera.get_params()))
#
# # Вторая строка
#
# residualds_blocs = [
#     lambda cam, data: (
#         np.array(residual_reprojection_point(cam, data, group='point_to_point')) * (1 / 100),
#         'Ошибка проекции точек'
#     ),
#     lambda cam, data: (np.array(residual_line_length(cam, data, group='line_length', expected=4)) * (1),
#                        'Ошибка длины отрезков'),
#     # lambda cam, data: (
#     #     np.array(residual_interline_distance(cam, data, group='interline_distance', expected=4)) * (1),
#     #     'Ошибка межлинейного расстояния')
# ]
#
# camera_test.set_params_from_list([1065.05, -145.46, 60.81, 175.58, 0.0, 0.0, 15.0])
#
# refine = RefineOptimizer(
#     camera=camera_test,
#     residual_blocks=residualds_blocs,
#     mask=[0, 1, 2, 3, 6],
#     bounds=[[500, -360, -360, -360, 15],
#             [1500, 360, 360, 360, 40]],
#     method='trf'
# )
#
# refine.run(data=data)
# print("Delta 2", - np.array(camera_test.get_params()) + np.array(camera.get_params()))
#
# # Третья строка
#
# residualds_blocs = [
#     lambda cam, data: (
#         np.array(residual_reprojection_point(cam, data, group='point_to_point')) * (1 / 100),
#         'Ошибка проекции точек'
#     ),
#     # lambda cam, data: (np.array(residual_line_length(cam, data, group='line_length', expected=4)) * (1),
#     #                    'Ошибка длины отрезков'),
#     lambda cam, data: (
#         np.array(residual_interline_distance(cam, data, group='interline_distance', expected=4)) * (1),
#         'Ошибка межлинейного расстояния')
# ]
#
# camera_test.set_params_from_list([1065.05, -145.46, 60.81, 175.58, 0.0, 0.0, 15.0])
#
# refine = RefineOptimizer(
#     camera=camera_test,
#     residual_blocks=residualds_blocs,
#     mask=[0, 1, 2, 3, 6],
#     bounds=[[500, -360, -360, -360, 15],
#             [1500, 360, 360, 360, 40]],
#     method='trf'
# )
#
# refine.run(data=data)
# print("Delta 3", - np.array(camera_test.get_params()) + np.array(camera.get_params()))
#
# # Четвертая строка
#
# residualds_blocs = [
#     lambda cam, data: (
#         np.array(residual_reprojection_point(cam, data, group='point_to_point')) * (1 / 100),
#         'Ошибка проекции точек'
#     ),
#     lambda cam, data: (np.array(residual_line_length(cam, data, group='line_length', expected=4)) * (1),
#                        'Ошибка длины отрезков'),
#     lambda cam, data: (
#         np.array(residual_interline_distance(cam, data, group='interline_distance', expected=4)) * (1),
#         'Ошибка межлинейного расстояния')
# ]
#
# camera_test.set_params_from_list([1065.05, -145.46, 60.81, 175.58, 0.0, 0.0, 15.0])
#
# refine = RefineOptimizer(
#     camera=camera_test,
#     residual_blocks=residualds_blocs,
#     mask=[0, 1, 2, 3, 6],
#     bounds=[[500, -360, -360, -360, 15],
#             [1500, 360, 360, 360, 40]],
#     method='trf'
# )
#
# refine.run(data=data)
# print("Delta 4", - np.array(camera_test.get_params()) + np.array(camera.get_params()))
#
# # Пятая строка
#
residualds_blocs = [
    # lambda cam, data: (
    #     np.array(residual_reprojection_point(cam, data, group='point_to_point')) * (1 / 100),
    #     'Ошибка проекции точек'
    # ),
    lambda cam, data: (np.array(residual_line_length(cam, data, group='line_length', expected=4)) * (1),
                       'Ошибка длины отрезков'),
    lambda cam, data: (
        np.array(residual_interline_distance(cam, data, group='interline_distance', expected=4)) * (1),
        'Ошибка межлинейного расстояния')
]
#
# camera_test.set_params_from_list([1065.05, -145.46, 60.81, 175.58, 0.0, 0.0, 15.0])

refine = RefineOptimizer(
    camera=camera_test,
    residual_blocks=residualds_blocs,
    mask=[0, 6],
    bounds=[[500, 15],
            [1500, 40]],
    method='trf'
)

refine.run(data=data)
print("Delta 5", - np.array(camera_test.get_params()) + np.array(camera.get_params()))

# pipeline = CalibrationPipeline(
#     init_stage=vp_init,
#     refine_stages=[refine],
#     n_iter=1,
# )
#
# pipeline.run(camera=camera_test, data=data)

# from source.calibration.base import RESUALDS
# from calibration.debug import plot_residuals_comparison
#
# handles, labels = plt.gca().get_legend_handles_labels()
# unique = dict(zip(labels, handles))
# plt.legend(unique.values(), unique.keys())
# plot_residuals_comparison(RESUALDS)

# print("delta", - np.array(camera_test.get_params()) + np.array(camera.get_params()))
#
# ax.set_xlim(0, camera.size[1])
# ax.set_ylim(camera.size[0], 0)
# plt.legend()
# plt.show()
