import numpy as np

class Point:
    def __init__(self, coord_image, coord_real):
        self.coord_image = np.array(coord_image)  
        self.coord_real = np.array(coord_real)   
        
    @classmethod    
    def from_combined(self, coord):
        coord_image = coord[0:3]
        coord_real = coord[3:7]
        return cls(coord_image, coord_real)
    
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