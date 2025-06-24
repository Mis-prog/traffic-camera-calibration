from source import CalibrationPipeline, Camera, VanishingPointCalibration, \
    RefineOptimizer
from source.annotation_tools import load_lines, load_lines_from_json
from calibration.refine import residual_interline_distance, residual_parallel_group, \
    residual_reprojection_line, residual_reprojection_point, residual_line_length, compute_line_length
from calibration.debug import load_scene_gps, visualize_source, projection_line
import numpy as np
from source.annotation_tools import AnnotationParser
from calibration.debug import compute_alignment_and_metrics
from source.vp_detection import VanishingPointEstimatorManual
from source.calibration.base import RESUALDS
from calibration.debug import plot_residuals_comparison

camera = Camera('data/undistorted_output_one.jpg')

annotation_parser = AnnotationParser("data/data.json")
lines_vp1 = annotation_parser.get_lines_by_class("Межлинейное расстояние")
lines_vp3 = annotation_parser.get_lines_by_class("vp3")
vp1_manual = VanishingPointEstimatorManual().estimate(lines_vp1)
vp3_manual = VanishingPointEstimatorManual().estimate(lines_vp3)

vp_init = VanishingPointCalibration(camera, debug_save_path='data/vp.png')
vp_init.set_vanishing_points(vpX=vp1_manual, vpZ=vp3_manual)


def refine(camera):
    data_refine = {
        "Ошибка проекции точек": annotation_parser.get_points_with_gps_and_pixel("Ошибка проекции точек"),
        "Межлинейное расстояние": annotation_parser.get_lines_by_class("Межлинейное расстояние"),
        "Расстояние линий": annotation_parser.get_lines_by_class("Расстояние линий"),
    }

    resualds_blocks = [
        # lambda cam, data: (
        #     np.array(residual_reprojection_point(cam, data, group='Ошибка проекции точек',
        #                                          gps_origin=(54.725377, 55.941033))) * (1 / 200),
        #     'Ошибка проекции точек'
        # ),
        lambda cam, data: (
            np.array(residual_line_length(cam, data, group='Расстояние линий', expected=4)) * (1),
            'Расстояние линий'),
        lambda cam, data: (
            np.array(residual_interline_distance(cam, data, group='Межлинейное расстояние', expected=3.7)) * (1),
            'Межлинейное расстояние'),
    ]

    refine_1 = RefineOptimizer(
        camera=camera,
        residual_blocks=resualds_blocks,
        mask=[0, 2, 6],
        bounds=[[500, -360, 10],
                [1500, 360, 40]],
        # bounds=[[500, 10],
        #         [1500, 40]],
        method='trf',
        debug_save_path='data/grid.png',
        grid_range=(12, 12)
    )

    pipeline = CalibrationPipeline(
        init_stage=vp_init,
        refine_stages=[refine_1],
        n_iter=1,
    )

    pipeline.run(camera=camera, data=data_refine)

    # plot_residuals_comparison(RESUALDS)

    return camera


camera = refine(camera)

annotation_parser = AnnotationParser("data/data_report.json")

import matplotlib.pyplot as plt

crosswalk_lengths = [compute_line_length(camera, line)
                     for line in annotation_parser.get_lines_by_class("Длина пешеходного перехода")]
car_lengths = [compute_line_length(camera, line)
               for line in annotation_parser.get_lines_by_class("Длина автомобиля")]

real_lengths = {
    "Длина автомобиля": 4.5,  # в метрах
    "Длина пешеходного перехода": 4,
}


def compute_errors(predicted_lengths, true_length):
    abs_errors = [abs(pred - true_length) for pred in predicted_lengths]
    rel_errors = [abs(pred - true_length) / true_length * 100 for pred in predicted_lengths]
    return abs_errors, rel_errors


abs_car, rel_car = compute_errors(car_lengths, real_lengths["Длина автомобиля"])
abs_cross, rel_cross = compute_errors(crosswalk_lengths, real_lengths["Длина пешеходного перехода"])

print(np.min(abs_car), np.mean(abs_car), np.max(abs_car), np.min(rel_car), np.mean(rel_car), np.max(rel_car))
print(np.min(abs_cross), np.mean(abs_cross), np.max(abs_cross), np.min(rel_cross), np.mean(rel_cross), np.max(rel_cross))

# plt.figure(figsize=(10, 5))
# plt.boxplot([abs_cross, abs_car], labels=["Переход (абс. ошибка)", "Авто (абс. ошибка)"])
# plt.ylabel("Абсолютная ошибка (м)")
# plt.title("Абсолютная ошибка измерения длины")
# plt.grid(True)
# plt.show()

# plt.figure(figsize=(10, 5))
# plt.boxplot([rel_cross, rel_car], labels=["Переход (отн. ошибка)", "Авто (отн. ошибка)"])
# plt.ylabel("Относительная ошибка (%)")
# plt.title("Относительная ошибка измерения длины")
# plt.grid(True)
# plt.show()
