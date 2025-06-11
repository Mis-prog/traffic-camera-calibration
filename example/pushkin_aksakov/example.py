from source import CalibrationPipeline, Camera, VanishingPointCalibration, \
    RefineOptimizer
from source.annotation_tools import load_lines, load_lines_from_json
from calibration.refine import residual_interline_distance, residual_parallel_group, \
    residual_reprojection_line
from calibration.debug import load_scene_gps, visualize_source

import numpy as np

camera = Camera('image/pattern_corrected_image.png')

vp1 = [3974.185, -248.69977]
vp2 = [768.4042, 2362.912]
vp3 = [-24.940735, -669.0249]
vps_auto = np.array([vp1, vp3, vp2])

# Набор найденный через RANSAK
# vp1_new = [3.535e+03, -1.270e+02]
# vp2_new = [164.36434109, -476.74418605]
# vps_auto_new = np.array([vp1_new, vp2_new])

vp_init = VanishingPointCalibration(camera, debug_save_path='image/vp.png')
vp_init.set_vanishing_points(*vps_auto)


def back_refine():
    """
    Параметры камеры [934.15, -158.11, 51.84, 172.31, 0.0, 0.0, 20.89] (не оптимизировал углы)
    """
    global camera
    data = {
        "dist_between_line_1": load_lines('marked/dist_between_line_1.json'),
        "dist_between_line_2": load_lines('marked/dist_between_line_2.json'),
        "lane_lines": load_lines('marked/parallel_line_1.json'),
        "vertical_lines": load_lines('marked/vertical_lines.json'),
    }
    resualds_blocks = [
        lambda cam, data: residual_interline_distance(cam, data, group="dist_between_line_1", expected=9),
        lambda cam, data: residual_interline_distance(cam, data, group="dist_between_line_2", expected=7),
        lambda cam, data: residual_parallel_group(cam, data, group="lane_lines"),
    ]
    refiner_1 = RefineOptimizer(camera=camera,
                                residual_blocks=resualds_blocks,
                                mask=[0],
                                bounds=[(700, 1500)],
                                debug_save_path='image/grid_back_1.png',
                                gps_origin=(54.723767, 55.933369),
                                method="minimize",
                                )

    refiner_2 = RefineOptimizer(camera=camera,
                                residual_blocks=resualds_blocks,
                                mask=[6],
                                bounds=[(5, 30)],
                                debug_save_path='image/grid_back_2.png',
                                gps_origin=(54.723767, 55.933369),
                                method="minimize",
                                )

    pipeline = CalibrationPipeline(
        init_stage=vp_init,
        refine_stages=[refiner_1, refiner_2],
        n_iter=20
    )
    camera = pipeline.run(camera, data)


# back_refine()  # Дооптимизация через обратную проекцию


def direct_refine():
    global camera
    data = {"lines_gps_and_pixel": load_lines_from_json('marked/lines_gps_to_pixel.json')
            }

    resualds_blocks = [
        lambda cam, data: residual_reprojection_line(cam, data, group="lines_gps_and_pixel",
                                                     gps_origin=(54.723603, 55.933098)),
    ]

    refiner_1 = RefineOptimizer(camera=camera,
                                residual_blocks=resualds_blocks,
                                debug_save_path='image/grid_direct_1.png',
                                mask=[0, 1, 2, 3, 6],
                                bounds=([800, -360, -360, -360, 5],
                                        [2000, 360, 360, 360, 30]),
                                )

    # refiner_2 = RefineOptimizer(camera=camera,
    #                             residual_blocks=resualds_blocks,
    #                             debug_save_path='image/',
    #                             mask=[0, 1, 2, 3],
    #                             )

    pipeline = CalibrationPipeline(
        init_stage=vp_init,
        refine_stages=[refiner_1],
        n_iter=1
    )
    camera = pipeline.run(camera, data)


direct_refine()  # Дооптимизация через прямую проекцию


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


# Разметка данных
# from utils.data_markup_tool import LineAnnotationTool
#
# line_tool = LineAnnotationTool("image/pattern_corrected_image.png","marked","vertical_lines.json")
# line_tool.run()


# Тесты
# from source.calibration.debug import visualize_grid_debug
# from source.core import PointND
# from utils.gps_connection_world import gps_to_enu, enu_to_gps
#
# gps_origin = (54.723767, 55.933369)
# camera.set_params_from_list([1263.28, -142.97, 51.84, 172.31, 0.0, 0.0, 28.88])
# visualize_grid_debug(camera, PointND(camera.intrinsics.get_main_point()))
#
# point = - camera.project_back(PointND([775.49946776, 886.09295195])).get()
# print(point)
# # point = [ -9.72, -15.13]
# enu = enu_to_gps(*point[:2], gps_origin[0], gps_origin[1])
# print(enu)
