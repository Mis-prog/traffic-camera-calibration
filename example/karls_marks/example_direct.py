import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


import matplotlib.pyplot as plt

from source import CalibrationPipeline, Camera, VanishingPointCalibration, \
    RefineOptimizer, PointND
from source.calibration.utils import load_lines, load_lines_from_json, extract_direction_vectors_from_lines
from source.calibration.refine import residual_interline_distance, residual_line_length
from source.calibration.debug import load_scene_gps, visualize_source

from source.vp_detection import VanishingPointEstimatorManual

import numpy as np

lines_vp1 = load_lines("marked/horizontal_lines.json")
lines_vp3 = load_lines("marked/vertical_lines.json")

vp1_manual = VanishingPointEstimatorManual().estimate(lines_vp1)
vp3_manual = VanishingPointEstimatorManual().estimate(lines_vp3)

vps_manual = np.array([vp1_manual, vp3_manual])

camera = Camera('data/pattern_corrected_image.png')

vp_init = VanishingPointCalibration(camera, debug_save_path='data/vp.png')
vp_init.set_vanishing_points(vpX=vps_manual[0], vpZ=vps_manual[1])


