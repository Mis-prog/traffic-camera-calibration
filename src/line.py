from .point2D import Point2D
from .point3D import Point3D


class Line:
    def __init__(self, start_2D: Point2D, start_3D: Point3D, end_2D: Point2D, end_3D: Point3D):
        self.start_2D = start_2D
        self.start_3D = start_3D
        self.end_2D = end_2D
        self.end_3D = end_3D
