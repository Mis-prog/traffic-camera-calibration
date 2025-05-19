from abc import ABC, abstractmethod
from core.camera import Camera


class Calibration(ABC):
    def __init__(self, camera: Camera = None):
        self.camera = camera

    @abstractmethod
    def run(self, data: dict) -> Camera:
        pass
