from point import Point
import numpy as np 

class Line:
    def __init__(self, point_start : Point, point_end : Point):
        self.point_start = point_start
        self.point_end = point_end
        self.intersection_X = None
    
    def set_intersection(self, X):
        self.intersection_X = X

class PointToPoint:
    def __init__(self):
        pass