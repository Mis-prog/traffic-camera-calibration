from source import CalibrationPipeline, Camera, VanishingPointCalibration, DirectProjectionOptimizer, \
    BackProjectionOptimizer
from source.utils import load_lines
from source.calibration.debug import visualize_source
from source.utils import LineAnnotationTool
from source.calibration.refine.back.error_funk import residual_interline_distance, residual_parallel_group

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
vp_init.set_vanishing_points(vps_auto[0], vpZ=vps_auto[2])

refiner = BackProjectionOptimizer(camera, debug_save_path='image/')

data = {
    "dist_between_line_1": load_lines('back_marked/dist_between_line_1.json'),
    "dist_between_line_2": load_lines('back_marked/dist_between_line_2.json'),
    "lane_lines": load_lines('back_marked/parallel_line_1.json'),
}

resualds_blocks = [
    lambda cam, data: residual_interline_distance(cam, data, group="dist_between_line_1", expected=8),
    lambda cam, data: residual_interline_distance(cam, data, group="dist_between_line_2", expected=5.5),
    lambda cam, data: residual_parallel_group(cam, data, group="lane_lines"),
]

pipeline = CalibrationPipeline(vp_init, refiner)
mask = [0, 4, 5, 6]
bounds = ([900, -35, -35, 4], [2000, 35, 35, 35])
camera = pipeline.run(camera, data, method="trf", resuals_blocks=resualds_blocks, mask=mask, bounds=bounds)


# Визуализация данных
# visualize_source(data, camera.get_image())

# Разметка данных
# tool = LineAnnotationTool("image/pattern_corrected_image.png", "back_marked/", 'parallel_line_1.json')
# tool.run()
