from source import CalibrationPipeline, Camera, VanishingPointCalibration, DirectProjectionOptimizer, \
    BackProjectionOptimizer
from source.utils import load_lines
from source.calibration.debug import visualize_source
from source.utils import LineAnnotationTool
from source.calibration.refine.back.error_funk import residual_interline_distance

import numpy as np

camera = Camera('image/pattern_corrected_image.png')
camera.set_params_from_list([1419.59, -142.56, 49.5, -185.62, -12.82, -18.38, 30.63])

vp1 = [3974.185, -248.69977]
vp2 = [768.4042, 2362.912]
vp3 = [-24.940735, -669.0249]
vps_auto = np.array([vp1, vp3, vp2])
vp_init = VanishingPointCalibration(camera, debug_save_path='image/vp.png')
vp_init.set_vanishing_points(vps_auto[0], vpZ=vps_auto[2])

refiner = BackProjectionOptimizer(camera, debug_save_path='image/')

data = {
    "dist_between_line_1": load_lines('back_marked/dist_between_line_1.json'),
    "dist_between_line_2": load_lines('back_marked/dist_between_line_2.json'),
}

resualds_blocks = [
    lambda cam, data: residual_interline_distance(cam, data, group="dist_between_line_1", expected=8),
    lambda cam, data: residual_interline_distance(cam, data, group="dist_between_line_2", expected=6),
]

pipeline = CalibrationPipeline(vp_init, refiner)
camera = pipeline.run(camera, data, method="trf", resuals_blocks=resualds_blocks)

# Визуализация данных
# visualize_source(data,camera.get_image())

# Разметка данных
# tool = LineAnnotationTool("image/pattern_corrected_image.png","back_marked/",'dist_between_line_2.json')
# tool.run()
