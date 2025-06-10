# import sys
# import os
#
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import numpy as np
import matplotlib.pyplot as plt

from source import CalibrationPipeline, Camera, VanishingPointCalibration, \
    RefineOptimizer, PointND
from source.calibration.utils import load_lines, load_lines_from_json, extract_direction_vectors_from_lines
from source.calibration.refine import residual_interline_distance, residual_line_length, residual_reprojection_line
from source.calibration.debug import load_scene_gps, visualize_source, generate_yandex_maps_url, \
    compute_alignment_and_metrics
from source.vp_detection import VanishingPointEstimatorManual
from source.calibration.utils import gps_to_enu, enu_to_gps
from source.annotation_tools import AnnotationParser

# Точки схода
# Фокусное расстояние и ориентация
annotation_parser = AnnotationParser("data/data_full_new.json")

lines_vp1 = annotation_parser.get_lines_by_class("vp1")
lines_vp3 = annotation_parser.get_lines_by_class("vp3")

vp1_manual = VanishingPointEstimatorManual().estimate(lines_vp1)
vp3_manual = VanishingPointEstimatorManual().estimate(lines_vp3)

vps_manual = np.array([vp1_manual, vp3_manual])

camera = Camera('data/pattern_corrected_image.png')

vp_init = VanishingPointCalibration(camera, debug_save_path='data/vp.png')
vp_init.set_vanishing_points(vpX=vps_manual[0], vpZ=vps_manual[1])


def back_refine(camera):
    """
    Результататы для перекрестка
    [899.24, -13.76, 48.15, -164.42, 0.0, 0.0, 20.02]
    """
    global annotation_parser

    data = {
        "Пешеходный переход 1": annotation_parser.get_lines_by_class("Пешеходный переход 1"),
        "Пешеходный переход 2": annotation_parser.get_lines_by_class("Пешеходный переход 2"),
        "Пешеходный переход 3": annotation_parser.get_lines_by_class("Пешеходный переход 3"),
        "Дорожные линии 2": annotation_parser.get_lines_by_class("Дорожные линии 2"),
    }
    resualds_blocks_first = [
        lambda cam, data: residual_interline_distance(cam, data, group="Пешеходный переход 1", expected=3.8),
        lambda cam, data: residual_interline_distance(cam, data, group="Пешеходный переход 2", expected=3.8),
        lambda cam, data: residual_interline_distance(cam, data, group="Пешеходный переход 3", expected=3.8),
        lambda cam, data: residual_interline_distance(cam, data, group="Дорожные линии 2", expected=3.25),
        # lambda cam, data: residual_line_length(cam, data, group="Пешеходный переход 1", expected=24),
        # lambda cam, data: residual_line_length(cam, data, group="pedestrian crossing 2", expected=24),
    ]
    refiner_1 = RefineOptimizer(
        camera=camera,
        residual_blocks=resualds_blocks_first,
        mask=[6],
        bounds=[(5, 30)],
        debug_save_path='data/grid_back_1.png',
        method="minimize",
    )

    refiner_2 = RefineOptimizer(
        camera=camera,
        residual_blocks=resualds_blocks_first,
        mask=[0],
        bounds=[(700, 1500)],
        debug_save_path='data/grid_back_2.png',
        method="minimize",
    )
    pipeline = CalibrationPipeline(
        init_stage=vp_init,
        refine_stages=[refiner_1, refiner_2],
        n_iter=20
    )

    camera = pipeline.run(camera, data)

    # camera.set_params_from_list([882.8, -13.76, 48.15, -164.42, 0.0, 0.0, 18.5])
    #
    # from source.calibration.debug import visualize_grid_debug, visualize_grid_gps_debug
    # point_start = PointND(camera.intrinsics.get_main_point(), add_weight=True)
    # visualize_grid_debug(camera, point_start, save_path="data/grid_back_2.png", grid_range=12,
    #                      grid_step=1)
    return camera


# camera = back_refine(camera)

# Метрика
# gps_control = annotation_parser.get_points_with_gps_and_pixel("Контрольные GPS точки")
# point_image, point_gps = [], []
# for point in gps_control:
#     _point_image, _point_gps = point["pixel"], point["gps"]
#     print(_point_image,_point_gps)
#     point_image.append(_point_image)
#     point_gps.append(_point_gps)
#
# compute_alignment_and_metrics(point_image, point_gps, 54.725378, 55.941036, camera)

"""
- Проблема с масштабом
- Возможно проблема в углах.
"""


def direct_refine(camera):
    """
    Результаты для перекрестка

    """
    gps_origin = (54.725378, 55.941036)

    data = {
        "Пешеходный переход 1": annotation_parser.get_lines_with_gps_and_pixel("Пешеходный переход 1"),
        "Пешеходный переход 2": annotation_parser.get_lines_with_gps_and_pixel("Пешеходный переход 2"),
        "Дорожные линии": annotation_parser.get_lines_with_gps_and_pixel("Дорожные линии"),
    }

    residual_blocks_first = [
        lambda cam, data: residual_reprojection_line(cam, data, group="Пешеходный переход 1",
                                                     gps_origin=gps_origin),
        lambda cam, data: residual_reprojection_line(cam, data, group="Пешеходный переход 2",
                                                     gps_origin=gps_origin),
        lambda cam, data: residual_reprojection_line(cam, data, group="Дорожные линии",
                                                     gps_origin=gps_origin),
    ]

    refiner_1 = RefineOptimizer(
        camera=camera,
        residual_blocks=residual_blocks_first,
        debug_save_path='data/grid_direct_1.png',
        mask=[1],
        bounds=([-180],
                [180]),
        # bounds=[(-360, 360), (-360, 360), (-360, 360), (5, 30)],
        # method="minimize",
    )

    refiner_2 = RefineOptimizer(
        camera=camera,
        residual_blocks=residual_blocks_first,
        debug_save_path='data/grid_direct_2.png',
        mask=[2],
        bounds=([-180],
                [180]),
        # bounds=[(-360, 360), (-360, 360), (-360, 360), (5, 30)],
        # method="minimize",
    )

    refiner_3 = RefineOptimizer(
        camera=camera,
        residual_blocks=residual_blocks_first,
        debug_save_path='data/grid_direct_3.png',
        mask=[3],
        bounds=([-180],
                [180]),
        # bounds=[(-360, 360), (-360, 360), (-360, 360), (5, 30)],
        # method="minimize",
    )

    refiner_4 = RefineOptimizer(
        camera=camera,
        residual_blocks=residual_blocks_first,
        debug_save_path='data/grid_direct_4.png',
        mask=[6],
        bounds=([5],
                [30]),
        # bounds=[(-360, 360), (-360, 360), (-360, 360), (5, 30)],
        # method="minimize",
    )

    refiner_5 = RefineOptimizer(
        camera=camera,
        residual_blocks=residual_blocks_first,
        debug_save_path='data/grid_direct_5.png',
        mask=[0],
        bounds=([700],
                [2000]),
        # bounds=[(-360, 360), (-360, 360), (-360, 360), (5, 30)],
        # method="minimize",
    )

    # refiner_second = RefineOptimizer(
    #     camera=camera,
    #     residual_blocks=residual_blocks_first,
    #     debug_save_path='data/grid_direct_2.png',
    #     mask=[0],
    #     bounds=([800],
    #             [2000])
    # )

    pipeline = CalibrationPipeline(
        init_stage=vp_init,
        refine_stages=[refiner_1, refiner_2, refiner_3, refiner_4, refiner_5],
        n_iter=10
    )

    camera = pipeline.run(camera, data)

    #
    #
    # world_point = []
    # for line in data['Пешеходный переход 1']:
    #     p1, p2 = line['gps']
    #     world_point.append(p1)
    #     world_point.append(p2)
    #
    # for line in data['Пешеходный переход 2']:
    #     p1, p2 = line['gps']
    #     world_point.append(p1)
    #     world_point.append(p2)
    #
    # for line in data['Дорожные линии']:
    #     p1, p2 = line['gps']
    #     world_point.append(p1)
    #     world_point.append(p2)
    #
    # print(generate_yandex_maps_url(world_point))

    return camera

# camera = direct_refine(camera)
