import numpy as np 

class Point:
    def __init__(self):
        self.coord_image = []
        self.coord_real = []
        self.w = 1
      
    def set_w(self, w):
        self.w = w
        
    def get_real(self):
        if self.coord_real:
            return np.array(self.coord_real) / self.w
        return np.array([])
    
    def get_real_full(self):
        if self.coord_real:
            return np.array(self.coord_real + [self.w])
        return np.array([])

    def get_image(self):
        if self.coord_image:
            return np.array(self.coord_image) / self.w
        return np.array([])

    def get_image_full(self):
        if self.coord_image:
            return np.array(self.coord_image + [self.w])
        return np.array([])