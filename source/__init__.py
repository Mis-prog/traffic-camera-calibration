"""
road_camera_calibration_toolkit
~~~~~~~~~~~~~~~~~~~~
Библиотека для калибровки камеры видеонаблюдения за дорожным движением на основе точек схода, структурных ограничений сцены
и данных с GPS.
"""

from .calibration import CalibrationPipeline
from .calibration import RefineOptimizer
from .core import Camera, PointND
from .calibration import VanishingPointCalibration

__all__ = [
    "CalibrationPipeline",
    "RefineOptimizer",
    "Camera",
    "VanishingPointCalibration",
    "PointND",
]

__version__ = "0.2.0"
__author__ = "Акмурзин Михаил"
__email__ = "akmurzinmihail@gmail.com"