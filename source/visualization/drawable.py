from abc import ABC, abstractmethod


class Drawable(ABC):
    @abstractmethod
    def draw(self, ax_or_image):
        pass
