from abc import ABC, abstractmethod
from core.camera import Camera


class Calibration(ABC):
    def __init__(self, camera: Camera = None, debug_save_path: str = None):
        self.camera = camera
        self.debug_save_path = debug_save_path

    @abstractmethod
    def run(self, data: dict, **kwargs) -> Camera:
        pass
