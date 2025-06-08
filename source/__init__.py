"""
calibration_toolkit
~~~~~~~~~~~~~~~~~~~~

Библиотека для калибровки камеры на основе точек схода, структурных ограничений сцены
и дооптимизации ориентации. Поддерживает ручную, автоматическую и геометрическую настройку.
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
__description__ = "Модуль для калибровки камеры и дооптимизации параметров по точкам схода и структуре сцены."