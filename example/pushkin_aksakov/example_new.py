from source import CalibrationPipeline, Camera, VanishingPointCalibration, DirectProjectionOptimizer

import matplotlib.pyplot as plt

camera = Camera('image/pattern_corrected_image.png')
vp_init = VanishingPointCalibration(camera)
vp_init.set_vanishing_points(vpX=[3974.185, -248.69977], vpZ=[768.4042, 2362.912])

refiner = DirectProjectionOptimizer(camera)

pipeline = CalibrationPipeline(vp_init, refiner)
lines = []
camera = pipeline.run(camera, lines)
