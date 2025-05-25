from source import CalibrationPipeline, Camera, VanishingPointCalibration, \
    RefineOptimizer
from source.utils import load_lines, load_lines_from_json
from calibration.refine import residual_interline_distance, residual_parallel_group
from calibration.debug import load_scene_gps

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
    global camera
    data = {
        "dist_between_line_1": load_lines('marked/dist_between_line_1.json'),
        "dist_between_line_2": load_lines('marked/dist_between_line_2.json'),
        "lane_lines": load_lines('marked/parallel_line_1.json'),
    }
    resualds_blocks = [
        lambda cam, data: residual_interline_distance(cam, data, group="dist_between_line_1", expected=8),
        lambda cam, data: residual_interline_distance(cam, data, group="dist_between_line_2", expected=5.5),
        lambda cam, data: residual_parallel_group(cam, data, group="lane_lines"),
    ]
    refiner = RefineOptimizer(camera=camera,
                              residual_blocks=resualds_blocks,
                              mask=[0, 6],
                              bounds=([900, 5], [2000, 30]),
                              debug_save_path='image/')
    pipeline = CalibrationPipeline([vp_init, refiner])
    mask = [0, 6]
    bounds = ([900, 4], [2000, 35])
    camera = pipeline.run(camera, data)


back_refine()  # Дооптимизация через обратную проекцию


def direct_refine():
    global camera
    refiner = RefineOptimizer(camera, debug_save_path='image/')
    print(load_lines_from_json('marked/lines_gps_to_pixel.json'))


# direct_refine() # Дооптимизация через прямую проекцию


def debug_gps():
    import matplotlib.pyplot as plt
    ref_lat, ref_lon = 54.723767, 55.933369
    image = load_scene_gps(ref_lon, ref_lat, zoom=19)
    image_np = np.array(image)  # вот здесь преобразование
    print(image_np.shape)
    plt.imshow(image)
    plt.scatter(650 / 2, 450 / 2)
    plt.show()

# debug_gps()
