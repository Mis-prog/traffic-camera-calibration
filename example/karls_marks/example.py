from source import CalibrationPipeline, Camera, VanishingPointCalibration, \
    RefineOptimizer
from source.utils import load_lines, load_lines_from_json
from calibration.refine import residual_interline_distance, residual_parallel_group, \
    residual_reprojection_line
from calibration.debug import load_scene_gps, visualize_source

from vp_detection import VanishingPointEstimatorManual

# Разметка данных
# from utils.data_markup_tool import LineAnnotationTool
#
# line_tool = LineAnnotationTool("image/pattern_corrected_image.png","marked","dist_ between_line_4.json")
# line_tool.run()

import numpy as np

lines_vp1 = load_lines("marked/horizontal_lines.json")
lines_vp3 = load_lines("marked/vertical_lines.json")
#
vp1_manual = VanishingPointEstimatorManual().estimate(lines_vp1)
vp3_manual = VanishingPointEstimatorManual().estimate(lines_vp3)
#
vps_manual = np.array([vp1_manual, vp3_manual])
#
camera = Camera('image/pattern_corrected_image.png')
#
# image = camera.get_image()
#
# import matplotlib.pyplot as plt
# plt.imshow(image)
# plt.scatter(vps_manual[0, 0], vps_manual[0, 1], c='r', label='Точка схода для направления X')
# plt.scatter(vps_manual[1, 0], vps_manual[1, 1], c='b', label='Точка схода для направления Z')


# for (x1, y1), (x2, y2) in lines_vp1:
#     plt.plot([x1, x2], [y1, y2], color='red', linewidth=2)
#
# for (x1, y1), (x2, y2) in lines_vp3:
#     plt.plot([x1, x2], [y1, y2], color='blue', linewidth=2)
# plt.legend()
# plt.show()


vp_init = VanishingPointCalibration(camera, debug_save_path='image/vp.png')
#
vp_init.set_vanishing_points(vpX=vps_manual[0], vpZ=vps_manual[1])

data = {
    "dist_between_line_1": load_lines('marked/dist_ between_line_1.json'),
    "dist_between_line_2": load_lines('marked/dist_ between_line_2.json'),
    "dist_between_line_3": load_lines('marked/dist_ between_line_3.json'),
    "dist_between_line_4": load_lines('marked/dist_ between_line_4.json'),
}

resualds_blocks = [
    lambda cam, data: residual_interline_distance(cam, data, group="dist_between_line_1", expected=11.5),
    lambda cam, data: residual_interline_distance(cam, data, group="dist_between_line_2", expected=4),
    lambda cam, data: residual_interline_distance(cam, data, group="dist_between_line_3", expected=4),
    lambda cam, data: residual_interline_distance(cam, data, group="dist_between_line_4", expected=4),
]

refiner_first = RefineOptimizer(camera=camera,
                                    residual_blocks=resualds_blocks,
                                    mask=[0, 6],
                                    bounds=([800, 5], [2000, 30]),
                                    debug_save_path='image/',
                                    )

pipeline = CalibrationPipeline([vp_init, refiner_first])
camera = pipeline.run(camera, data)
