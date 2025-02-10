import numpy as np


class Point3D:
    def __init__(self, coord):
        self.coord = coord

    @classmethod
    def from_homogeneous(cls, coord):
        if len(coord) == 3:
            coord = np.append(coord, 1)
            return cls(coord=coord)

    def set(self, coord):
        self.coord = coord

    # по умолчанию неоднородные координаты
    def get(self, out_homogeneous=False):
        if out_homogeneous:
            return self.coord
        else:
            return np.array(self.coord[:-1]) / self.coord[-1]