import numpy as np


class PointND:
    def __init__(self, coord):
        coord = np.asarray(coord)
        if len(coord) + 1 in [3, 4]:
            coord = np.append(coord, 1)
        self.coord = coord

    def set(self, coord):
        self.coord = np.append(coord, 1) if len(coord) + 1 == len(self.coord) else coord

    def get(self, out_homogeneous=False):
        return self.coord if out_homogeneous else self.coord[:-1] / self.coord[-1]

    def get_type(self):
        dim = len(self.coord) - 1
        return f"{dim}D"

    def set_Z(self, z):
        if len(self.coord) > 3:
            self.coord[2] = z
        else:
            raise ValueError("Объект не является 3D точкой")