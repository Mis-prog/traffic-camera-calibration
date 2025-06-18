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

camera = Camera('image/undistorted_output_one.jpg')

annotation_parser = AnnotationParser("marked/data_full_new.json")
lines_vp1 = annotation_parser.get_lines_by_class("vp1")
lines_vp3 = annotation_parser.get_lines_by_class("vp3")
vp1_manual = VanishingPointEstimatorManual().estimate(lines_vp1)
vp3_manual = VanishingPointEstimatorManual().estimate(lines_vp3)

vp_init = VanishingPointCalibration(camera, debug_save_path='image/vp.png')
vp_init.set_vanishing_points(vpX=vp1_manual, vpZ=vp3_manual)


def refine(camera):
    data_refine = {
        "Растояние из точки в точку": annotation_parser.get_points_with_gps_and_pixel("Растояние из точки в точку"),
        "Растояние от точки до точки линии": annotation_parser.get_lines_by_class("Растояние от точки до точки линии"),
    }

    resualds_blocks = [
        lambda cam, data: (
            np.array(residual_reprojection_point(cam, data, group='Растояние из точки в точку',
                                                 gps_origin=(54.723617, 55.933152))) * (1 / 100),
            'Растояние из точки в точку'
        ),
        lambda cam, data: (
            np.array(residual_line_length(cam, data, group='Растояние от точки до точки линии', expected=4)) * (1),
            'Растояние от точки до точки линии'),
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

    pipeline.run(camera=camera, data=data_refine)

    plot_residuals_comparison(RESUALDS)

    return camera


camera = refine(camera)

point_control = annotation_parser.get_points_with_gps_and_pixel("Растояние из точки в точку")
point_image, point_gps = [], []
for point in point_control:
    _point_image, _point_gps = point["pixel"], point["gps"]
    # print(_point_image, _point_gps)
    point_image.append(_point_image)
    point_gps.append(_point_gps)

data = compute_alignment_and_metrics(point_image, point_gps, 54.723617, 55.933152, camera, save_path="direct.html")
