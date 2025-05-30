from abc import ABC, abstractmethod


class Detector(ABC):

    def run(self, **kwargs):
        pass
