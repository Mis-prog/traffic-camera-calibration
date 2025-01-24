import numpy as np
from  scipy.optimize import least_squares

from camera import Camera 
from point import Point

class Optimizer:
  def __init__(self, _camera:Camera):
    self.camera = _camera 

  def funk_error(self,line_known, line_predict):
    pointknownStart, pointknownEnd = line_known
    pointpredictStart, pointpredictEnd = line_predict
    
    error = (
        np.sqrt((pointknownStart.get_image()[0] - pointpredictStart.get_image()[0])**2 +
                (pointknownStart.get_image()[1] - pointpredictStart.get_image()[1])**2)
        + np.sqrt((pointknownEnd.get_image()[0] - pointpredictEnd.get_image()[0])**2 +
                  (pointknownEnd.get_image()[1] - pointpredictEnd.get_image()[1])**2)
    )
    return error
  
  def residuals(self,params, lines):
    residuals = []
    for line in lines:
      line_start, line_end = line
      point_known_start = Point()
      point_known_start.set_coord_image(line_start[0:2])
      point_known_start.set_coord_real(line_start[2:5])
      point_known_end = Point()
      point_known_end.set_coord_image(line_end[0:2])
      point_known_end.set_coord_real(line_end[2:5])

        
      _point_predict_start = self.camera.direct_transform(point_known_start.get_real_full(),params)
      _point_predict_end = self.camera.direct_transform(point_known_end.get_real_full(),params)
      
      point_predict_start = point_known_start
      point_predict_start.set_coord_image(_point_predict_start[0:2])
      
      point_predict_end = point_known_end
      point_predict_end.set_coord_image(_point_predict_end[0:2])
        
      error = self.funk_error(
          [point_known_start, point_known_end],
          [point_predict_start, point_predict_end]
      )
      residuals.append(error)
    
    return residuals
  
  def optimize(self, lines):
    angles = self.camera.get_R(angle_output=True)
    x0 = [self.init.get_f(), angles[0], angles[1], angles[2], 1]
    result = least_squares(self.residuals, x0, args=(lines,), method='lm')
    return result