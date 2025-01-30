import numpy as np


class Point:
    def __init__(self, coord_image, coord_real):
        self.coord_image = np.array(coord_image)
        self.coord_real = np.array(coord_real)

    @classmethod
    def from_combined(cls, coord):
        coord_image = coord[0:3]
        coord_real = coord[3:7]
        return cls(coord_image, coord_real)

    @classmethod
    def copy(cls, other):
        return cls(
            coord_image=np.copy(other.coord_image),
            coord_real=np.copy(other.coord_real)
        )
    @classmethod
    def from_only_real(cls, coord):
        return cls([0, 0, 1], coord)

    @classmethod
    def from_only_image(cls, coord):
        return cls(coord, [0, 0, 0, 1])

    def set_image(self, coord_image):
        self.coord_image = np.array(coord_image)

    def set_real(self, coord_real):
        self.coord_real = np.array(coord_real)

    def get_real(self):
        return np.array(self.coord_real[:-1]) / self.coord_real[-1]

    def get_real_full(self):
        return np.array(self.coord_real)

    def get_image(self):
        return np.array(self.coord_image[:-1]) / self.coord_image[-1]

    def get_image_full(self):
        return np.array(self.coord_image)
