from abc import ABC, abstractmethod


class Detector(ABC):
    @abstractmethod
    def run(self, **kwargs):
        pass
