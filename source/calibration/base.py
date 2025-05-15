from abc import ABC, abstractmethod


class Calibration(ABC):
    def __init__(self, camera):
        self.camera = camera

    # @abstractmethod
    # def calibration(self, data):
    #     pass

    def __call__(self, data):
        return self.calibration(data)