from source import CalibrationPipeline, Camera, VanishingPointCalibration, DirectProjectionOptimizer

import matplotlib.pyplot as plt
import numpy as np

camera = Camera('image/pattern_corrected_image.png')


vp1 = [3974.185, -248.69977]
vp2 = [768.4042, 2362.912]
vp3 = [-24.940735, -669.0249]
vps_auto = np.array([vp1, vp3, vp2])
vp_init = VanishingPointCalibration(camera,debug=True)
vp_init.set_vanishing_points(*vps_auto)

refiner = DirectProjectionOptimizer(camera)

pipeline = CalibrationPipeline(vp_init, refiner)
lines = []
camera = pipeline.run(camera, lines, method="trf")
