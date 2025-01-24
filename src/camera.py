import numpy as np
import cv2
from scipy.spatial.transform import Rotation


class Camera:
  def __init__(self):
    self.size = None
    self.image = None
    self.tau = None
    
    self.A = np.zeros((3,3))
    self.R = np.zeros((3,3))
    self.T = np.zeros((3,1)).reshape(-1,1)

  
  def get_tau(self):
    return self.tau

  def load_image(self, path):
    self.image = cv2.imread(path)
    height, width, channels = self.image.shape
    self.size = [height, width] # высота и ширина
    self.tau = height / width

  # вычисление матрицы поворота
  def calc_R(self, euler_angles):
    rot = Rotation.from_euler('xyz', euler_angles, degrees=True)
    self.R = rot.as_matrix()

  def update_R(self, p):
    self.R =  np.vstack(p).transpose()
  
  def get_R(self, angle_output = False):
    if angle_output:
      return Rotation.from_matrix(self.R).as_euler('xyz', degrees=True)
    return self.R
  
  # вычисление столбца переноса
  def calc_T(self, h):
    self.T = np.array([0, 0, h]).reshape(-1,1)
    
  def get_T(self):
    return self.T
  
  # вычисление внутренней матрицы
  def calc_A(self, f):
    self.A = np.array([[f, 0, 0],
                     [0, f, 0],
                     [0, 0, 1]])
    
  # вычисление внутренней матрицы уточняющий способ 
  def calc_A_v2(self, f):
    self.A = np.array([[f, 0, 0],
                     [0, f * self.tau, 0],
                     [0, 0, 1]])
    
  def get_A(self):
    return self.A

 # прямое преобразование
  def direct_transform(self,point_real:Point, params = []):
    if len(params) > 0:
      self.calc_A_v2(params[0])
      self.calc_R(params[1:3])
      self.calc_T(params[4])
    
    T = self.T.reshape(-1, 1) 
    RT = np.hstack([self.R, self.T])
    AT = self.A @ RT
    return AT @ point_real.get_real_full()
  
  # обратное преобразование
  def back_transform(self,point_image:Point, params = []):
    if params:
      pass #todo 
    
    T = self.T.reshape(-1, 1) 
    RT = np.hstack([self.R, self.T])
    AT_inv = np.linalg.inv(self.A @ RT)
    return AT_inv @ point_image.get_image_full()