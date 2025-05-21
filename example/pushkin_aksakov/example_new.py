from source import CalibrationPipeline, Camera, VanishingPointCalibration, DirectProjectionOptimizer

import matplotlib.pyplot as plt
import numpy as np

camera = Camera('image/pattern_corrected_image.png')
camera.extrinsics.set_position(-12.82, -18.38, 30.63)

vp1 = [3974.185, -248.69977]
vp2 = [768.4042, 2362.912]
vp3 = [-24.940735, -669.0249]
vps_auto = np.array([vp1, vp3, vp2])
vp_init = VanishingPointCalibration(camera, debug_save_path='image/vp.png')
vp_init.set_vanishing_points(vps_auto[0], vpZ=vps_auto[2])

# camera.set_params_from_list([1419.59, -142.56, 49.5, -185.62, -12.82, -18.38, 30.63])

refiner = DirectProjectionOptimizer(camera, debug_save_path='image/')

pipeline = CalibrationPipeline(vp_init, refiner)
data = []
camera = pipeline.run(camera, data, method="trf")
