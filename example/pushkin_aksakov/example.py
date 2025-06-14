from source import CalibrationPipeline, Camera, VanishingPointCalibration, \
    RefineOptimizer
from source.annotation_tools import load_lines, load_lines_from_json
from calibration.refine import residual_interline_distance, residual_parallel_group, \
    residual_reprojection_line, orthogonal_to_plane_loss, parallel_to_plane_loss
from calibration.debug import load_scene_gps, visualize_source, projection_line

import numpy as np

camera = Camera('image/pattern_corrected_image.png')

# vp1 = [3974.185, -248.69977]
# vp2 = [768.4042, 2362.912]
# vp3 = [-24.940735, -669.0249]
# vps_auto = np.array([vp1, vp3, vp2])

# Набор найденный через RANSAK
vp1_new = [3.535e+03, -1.270e+02]
vp2_new = [164.36434109, -476.74418605]
vps_auto_new = np.array([vp1_new, vp2_new])

vp_init = VanishingPointCalibration(camera, debug_save_path='image/vp.png')
vp_init.set_vanishing_points(vpX=vps_auto_new[0], vpY=vps_auto_new[1])

from source.annotation_tools import AnnotationParser
from calibration.debug import compute_alignment_and_metrics

annotation_parser = AnnotationParser("marked/data_full.json")
point_control = annotation_parser.get_points_with_gps_and_pixel("Контрольные GPS точки")
point_image, point_gps = [], []
for point in point_control:
    _point_image, _point_gps = point["pixel"], point["gps"]
    # print(_point_image, _point_gps)
    point_image.append(_point_image)
    point_gps.append(_point_gps)


def back_refine(camera):
    """
    Параметры камеры [934.15, -158.11, 51.84, 172.31, 0.0, 0.0, 20.89] (не оптимизировал углы)
    """

    data = {
        "Перешеходный переход 1": annotation_parser.get_lines_by_class("Перешеходный переход 1"),
        "Перешеходный переход 2": annotation_parser.get_lines_by_class("Перешеходный переход 2"),
        "Перешеходный переход 3": annotation_parser.get_lines_by_class("Перешеходный переход 3"),
        "Перешеходный переход 4": annotation_parser.get_lines_by_class("Перешеходный переход 4"),
        "Расстояние между линиями": annotation_parser.get_lines_by_class("Расстояние между линиями"),
        "Расстояние между линиями 2": annotation_parser.get_lines_by_class("Расстояние между линиями 2"),
        "Вертикальные линии": annotation_parser.get_lines_by_class("Вертикальные линии"),
        "Горизонтальные линии": annotation_parser.get_lines_by_class("Горизонтальные линии"),
    }
    resualds_blocks_1 = [
        lambda cam, data: residual_interline_distance(cam, data, group="Перешеходный переход 1", expected=4),
        lambda cam, data: residual_interline_distance(cam, data, group="Перешеходный переход 2", expected=4),
        lambda cam, data: residual_interline_distance(cam, data, group="Перешеходный переход 3", expected=4),
        lambda cam, data: residual_interline_distance(cam, data, group="Перешеходный переход 4", expected=4),
        lambda cam, data: residual_interline_distance(cam, data, group="Расстояние между линиями", expected=3.2),
        lambda cam, data: residual_interline_distance(cam, data, group="Расстояние между линиями 2", expected=7),
    ]

    resualds_blocks_2 = [
        lambda cam, data: orthogonal_to_plane_loss(cam, data, group="Вертикальные линии"),
        lambda cam, data: parallel_to_plane_loss(cam, data, group="Горизонтальные линии"),
    ]

    refiner_1 = RefineOptimizer(camera=camera,
                                residual_blocks=resualds_blocks_1,
                                mask=[6],
                                # bounds=[(15, 40)],
                                bounds=[[12], [40]],
                                debug_save_path='image/grid_back_1.png',
                                gps_origin=(54.723767, 55.933369),
                                method="trf",
                                grid_range=10
                                )

    refiner_2 = RefineOptimizer(camera=camera,
                                residual_blocks=resualds_blocks_2,
                                mask=[2, 3],
                                # bounds=[(15, 40)],
                                bounds=[[1], [1700, 40]],
                                debug_save_path='image/grid_back_2.png',
                                gps_origin=(54.723767, 55.933369),
                                method="trf",
                                )

    # refiner_2 = RefineOptimizer(camera=camera,
    #                             residual_blocks=resualds_blocks_2,
    #                             mask=[2, 3],
    #                             bounds=[(40, 53), (170,180)],
    #                             # bounds=[[12], [40]],
    #                             debug_save_path='image/grid_back_2.png',
    #                             gps_origin=(54.723767, 55.933369),
    #                             method="minimize",
    #                             )

    pipeline = CalibrationPipeline(
        init_stage=vp_init,
        refine_stages=[
            refiner_1,
            # refiner_2
        ],
        n_iter=1
    )

    camera = pipeline.run(camera, data)

    return camera


camera = back_refine(camera)

data = compute_alignment_and_metrics(point_image, point_gps, 54.723617, 55.933152, camera, save_path="back.html")

projection_line(camera, annotation_parser.get_lines_with_gps_and_pixel("Размеченные линии"), 54.723617, 55.933152,
                save_path='image/projection_line_2.png', R=data["rotation_matrix"].T)


def direct_refine():
    """
    Параметры камеры 1167.74, -142.28, 49.46, 172.08, 0.0, 0.0, 30.37 погрешность 65 см
    """
    global camera
    data = {"lines_gps_and_pixel": load_lines_from_json('marked/lines_gps_to_pixel.json'),
            "Размеченные линии": annotation_parser.get_lines_with_gps_and_pixel("Размеченные линии")
            }

    print(data)

    resualds_blocks = [
        # lambda cam, data: residual_reprojection_line(cam, data, group="lines_gps_and_pixel",
        #                                              gps_origin=(54.723617, 55.933152)),
        lambda cam, data: residual_reprojection_line(cam, data, group="Размеченные линии",
                                                     gps_origin=(54.723617, 55.933152)),
    ]

    refiner_1 = RefineOptimizer(camera=camera,
                                residual_blocks=resualds_blocks,
                                debug_save_path='image/grid_direct_1.png',
                                mask=[0, 1, 2, 3, 6],
                                bounds=([800, -360, -360, -360, 13],
                                        [2000, 360, 360, 360, 35]),
                                # bounds=[(-180, 100), (0, 100), (150, 190)],
                                method="trf",
                                grid_range=10
                                )

    pipeline = CalibrationPipeline(
        init_stage=vp_init,
        refine_stages=[refiner_1],
        n_iter=1,
    )
    camera = pipeline.run(camera, data)

    projection_line(camera, annotation_parser.get_lines_with_gps_and_pixel("Размеченные линии"), 54.723617, 55.933152,
                    save_path='image/projection_line.png')

    return camera


camera = direct_refine()  # Дооптимизация через прямую проекцию
data = compute_alignment_and_metrics(point_image, point_gps, 54.723617, 55.933152, camera, save_path="direct.html")


def gibrid():
    global camera
    data = {
        "dist_between_line_1": load_lines('marked/dist_between_line_1.json'),
        "dist_between_line_2": load_lines('marked/dist_between_line_2.json'),
        "lane_lines": load_lines('marked/parallel_line_1.json'),
        "lines_gps_and_pixel": load_lines_from_json('marked/lines_gps_to_pixel.json')
    }
    resualds_blocks_first = [
        lambda cam, data: residual_interline_distance(cam, data, group="dist_between_line_1", expected=8),
        lambda cam, data: residual_interline_distance(cam, data, group="dist_between_line_2", expected=5.5),
        lambda cam, data: residual_parallel_group(cam, data, group="lane_lines"),
    ]
    refiner_first = RefineOptimizer(camera=camera,
                                    residual_blocks=resualds_blocks_first,
                                    mask=[0, 6],
                                    bounds=([900, 5], [2000, 30]),
                                    debug_save_path='image/')

    resualds_blocks_second = [
        lambda cam, data: residual_reprojection_line(cam, data, group="lines_gps_and_pixel",
                                                     gps_origin=(54.723767, 55.933369)),
    ]

    refiner_second = RefineOptimizer(camera=camera, residual_blocks=resualds_blocks_second, debug_save_path='image/')

    pipeline = CalibrationPipeline([vp_init, refiner_first, refiner_second])
    camera = pipeline.run(camera, data)

# gibrid()
