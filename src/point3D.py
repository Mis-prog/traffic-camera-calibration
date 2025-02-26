import numpy as np


# todo описать класс чтобы он принимал на вход вектора длины 3 для обратного преобразования
class Point3D:
    def __init__(self, coord):
        if len(coord) == 3:
            coord = np.append(coord, 1)
            self.coord = coord
        elif len(coord) == 4:
            self.coord = coord

    def set(self, coord):
        self.coord = coord

    def set_Z(self, z):
        self.coord[2] = z

    # по умолчанию неоднородные координаты
    def get(self, out_homogeneous=False):
        if out_homogeneous:
            return self.coord
        else:
            return np.array(self.coord[:-1]) / self.coord[-1]
