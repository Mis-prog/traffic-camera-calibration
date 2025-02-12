import numpy as np


# по умолчанию грузим гомогенные координаты
class Point2D:
    def __init__(self, coord):
        if len(coord) == 2:
            coord = np.append(coord, 1)
            self.coord = coord
        elif len(coord) == 3:
            self.coord = coord

    def set(self, coord):
        self.coord = coord

    def get(self, out_homogeneous=False):
        if out_homogeneous:
            return self.coord
        else:
            return self.coord[:-1] / self.coord[-1]
