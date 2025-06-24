from source import CalibrationPipeline, Camera, VanishingPointCalibration, \
    RefineOptimizer
from source.annotation_tools import load_lines, load_lines_from_json
from calibration.refine import residual_interline_distance, residual_parallel_group, \
    residual_reprojection_line, residual_reprojection_point, residual_line_length
from calibration.debug import load_scene_gps, visualize_source, projection_line
import numpy as np
from source.annotation_tools import AnnotationParser
from calibration.debug import compute_alignment_and_metrics
from source.vp_detection import VanishingPointEstimatorManual
from source.calibration.base import RESUALDS
from calibration.debug import plot_residuals_comparison
import matplotlib.pyplot as plt

camera = Camera('image/undistorted_output_one.jpg')

annotation_parser = AnnotationParser("marked/data_full_new.json")
lines_vp1 = annotation_parser.get_lines_by_class("vp1")
lines_vp3 = annotation_parser.get_lines_by_class("vp3")
vp1_manual = VanishingPointEstimatorManual().estimate(lines_vp1)
vp3_manual = VanishingPointEstimatorManual().estimate(lines_vp3)

# image = camera.get_image()
# plt.imshow(image)
#
# for line in lines_vp1:
#     line = np.array(line)
#     plt.plot(line[:, 0], line[:, 1], c = 'b')
#
# plt.scatter(*vp1_manual,c='b', label='Точки схода для направления X')
#
# for line in lines_vp3:
#     line = np.array(line)
#     plt.plot(line[:, 0], line[:, 1], c = 'r')
#
# plt.scatter(*vp3_manual,c='r',label='Точка схода для напраления Z')
# plt.legend()
# plt.show()


vp_init = VanishingPointCalibration(camera, debug_save_path='image/vp.png')
vp_init.set_vanishing_points(vpX=vp1_manual, vpZ=vp3_manual)

annotation_parser = AnnotationParser("marked/DATA_NEW.json")


#
def refine(camera):
    data_refine = {
        "Ошибка проекции точек": annotation_parser.get_points_with_gps_and_pixel("Ошибка проекции точек"),
        "Межлинейное расстояние": annotation_parser.get_lines_by_class("Межлинейное расстояние"),
        "Расстояние линий": annotation_parser.get_lines_by_class("Расстояние линий"),
    }

    resualds_blocks = [
        lambda cam, data: (
            np.array(residual_reprojection_point(cam, data, group='Ошибка проекции точек',
                                                 gps_origin=(54.723617, 55.933152))) * (1 / 100),
            'Ошибка проекции точек'
        ),
        lambda cam, data: (
            np.array(residual_line_length(cam, data, group='Расстояние линий', expected=4)) * (1),
            'Расстояние линий'),
        lambda cam, data: (
            np.array(residual_interline_distance(cam, data, group='Межлинейное расстояние', expected=3.2)) * (1),
            'Межлинейное расстояние'),
    ]

    refine = RefineOptimizer(
        camera=camera,
        residual_blocks=resualds_blocks,
        mask=[0, 1, 2, 3, 6],
        bounds=[[500, -360, -360, -360, 10],
                [1500, 360, 360, 360, 40]],
        method='trf',
        debug_save_path='image/grid.png'
    )

    pipeline = CalibrationPipeline(
        init_stage=vp_init,
        refine_stages=[refine],
        n_iter=1,
    )

    # pipeline.run(camera=camera, data=data_refine)

    camera.set_params_from_list([1098.35, -159.01, 48.63, 172.63, 0.0, 0.0, 15.0])

    print('С географической привязки')
    refine.run( data_refine)

    resualds_blocks = [
        # lambda cam, data: (
        #     np.array(residual_reprojection_point(cam, data, group='Ошибка проекции точек',
        #                                          gps_origin=(54.723617, 55.933152))) * (1 / 100),
        #     'Ошибка проекции точек'
        # ),
        lambda cam, data: (
            np.array(residual_line_length(cam, data, group='Расстояние линий', expected=4)) * (1),
            'Расстояние линий'),
        lambda cam, data: (
            np.array(residual_interline_distance(cam, data, group='Межлинейное расстояние', expected=3.2)) * (1),
            'Межлинейное расстояние'),
    ]

    refine = RefineOptimizer(
        camera=camera,
        residual_blocks=resualds_blocks,
        mask=[0,  6],
        bounds=[[500,  10],
                [1500, 40]],
        method='trf',
        debug_save_path='image/grid.png'
    )

    camera.set_params_from_list([1098.35, -159.01, 48.63, 172.63, 0.0, 0.0, 15.0])

    print('Без географической привязки')
    refine.run(data_refine)

    return camera


#
camera = refine(camera)
# #
# point_control = annotation_parser.get_points_with_gps_and_pixel("Контрольные точки")
# point_image, point_gps = [], []
# for point in point_control:
#     _point_image, _point_gps = point["pixel"], point["gps"]
#     # print(_point_image, _point_gps)
#     point_image.append(_point_image)
#     point_gps.append(_point_gps)
#
# point_control = annotation_parser.get_points_with_gps_and_pixel("Ошибка проекции точек")
# for point in point_control:
#     _point_image, _point_gps = point["pixel"], point["gps"]
#     # print(_point_image, _point_gps)
#     point_image.append(_point_image)
#     point_gps.append(_point_gps)
#
#
# data = compute_alignment_and_metrics(point_image, point_gps, 54.723617, 55.933152, camera, save_path="direct.html")
