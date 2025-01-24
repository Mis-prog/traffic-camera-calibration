import numpy as np 
from camera import Camera

# вычисление нормали к линии (вектора направления)
def _normal_vector(self,x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1

    normal = np.array([-dy, dx]) / np.sqrt(dx * dx + dy * dy)
    return normal

# поиск точек схода для набора линий
def _search_vanishing_point(lines):
    A = []
    b = []

    for line in lines:
        (x1, y1), (x2, y2) = line
        n = _normal_vector(x1, y1, x2, y2)
        A.append(n)
        b.append(np.dot(n, [x1, y1]))

    A = np.array(A)
    b = np.array(b)
    
    v = np.linalg.lstsq(A, b, rcond=None)[0]
    return v

# поиск точек схода для нескольких осей 
def  search_vanishing_points(lines):
    v = []
    for line in lines:
        _v = _search_vanishing_point(line)
        v.append(_v)
    return v
    
# вычисление нормализованный точек схода    
def calc_norm_vanishing_points(self, vx, vy, camera):
    px = np.linalg.inv(camera.get_A().transpose()) @ np.transpose(np.hstack([vx, 1]))
    py = np.linalg.inv(camera.get_A().transpose()) @ np.transpose(np.hstack([vy, 1]))
    pz = px * py
    return px, py, pz 

# вычисление фокусного расстояния
def calc_f(vx, vy, D = np.array([0, 0])):
    return np.sqrt(-np.dot((vx - D), (vy - D)))

def calc_f(vx, vy, camera:Camera):
    M = np.array([[1, 0], [0, camera.tau**(-2)]])
    return np.sqrt(- vx.T @ M @ vy)