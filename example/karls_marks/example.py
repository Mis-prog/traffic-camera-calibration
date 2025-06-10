import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import numpy as np
import matplotlib.pyplot as plt

from source import CalibrationPipeline, Camera, VanishingPointCalibration, \
    RefineOptimizer, PointND
from source.calibration.utils import load_lines, load_lines_from_json, extract_direction_vectors_from_lines
from source.calibration.refine import residual_interline_distance, residual_line_length
from source.calibration.debug import load_scene_gps, visualize_source
from source.vp_detection import VanishingPointEstimatorManual
from source.calibration.utils import gps_to_enu, enu_to_gps
from source.utils import AnnotationParser

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
    [781.26, -13.46, 48.12, -164.54, 0.0, 0.0, 17.26]
    """
    global annotation_parser

    data = {
        "Пешеходный переход 1": annotation_parser.get_lines_by_class("Переходный переход 1"),
        "Пешеходный переход 2": annotation_parser.get_lines_by_class("Пешеходный переход 2"),
        "Пешеходный переход 3": annotation_parser.get_lines_by_class("Пешеходный переход 3"),
        "Дорожные линии 2": annotation_parser.get_lines_by_class("Дорожные линии 2"),
    }
    resualds_blocks_first = [
        lambda cam, data: residual_interline_distance(cam, data, group="Пешеходный переход 1", expected=3.8),
        lambda cam, data: residual_interline_distance(cam, data, group="Пешеходный переход 2", expected=3.8),
        lambda cam, data: residual_interline_distance(cam, data, group="Пешеходный переход 3", expected=3.8),
        lambda cam, data: residual_interline_distance(cam, data, group="Дорожные линии 2", expected=3.25),
        # lambda cam, data: residual_line_length(cam, data, group="pedestrian crossing", expected=24),
        # lambda cam, data: residual_line_length(cam, data, group="pedestrian crossing 2", expected=24),
    ]
    refiner_first = RefineOptimizer(
        camera=camera,
        residual_blocks=resualds_blocks_first,
        mask=[6],
        bounds=[(5, 30)],
        debug_save_path='data/',
        method="minimize",
    )

    refiner_second = RefineOptimizer(
        camera=camera,
        residual_blocks=resualds_blocks_first,
        mask=[0],
        bounds=[(900, 2000)],
        debug_save_path='data/',
        method="minimize",
    )
    pipeline = CalibrationPipeline([vp_init, refiner_first, refiner_second])
    camera = pipeline.run(camera, data)

    return camera

camera = back_refine(camera)
"""
- Проблема с масштабом
- Возможно проблема в углах.
"""

def direct_refine(camera):
    """
    Результаты для перекрестка

    """
    data = {
        "point_to_point": None,
        "line_to_line": None,
    }

    residual_blocks_first = [

    ]

    refiner_first = RefineOptimizer(
        camera=camera,
        residual_blocks=residual_blocks_first,
    )

    return camera

# camera = direct_refine(camera)
