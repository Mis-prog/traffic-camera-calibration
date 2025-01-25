from camera import Camera
from optimizetion import Optimizer
from initsolution import calc_init_camera

Line_Y = [[[786, 689], [281, 515]], [[1061, 516], [213, 340]], [[1008, 421], [375, 311]], [[355, 264], [70, 238]], [[362, 223], [73, 211]]]
Line_X = [[[300, 513], [555, 185]], [[835, 677], [927, 264]], [[674, 117], [740, 13]], [[833, 192], [842, 158]], [[954, 142], [954, 38]]]

camera = calc_init_camera('../data/scene_from_crossroads_not_dist.png',[Line_X, Line_Y])
print(camera.get_A(),'\n',camera.get_R(),'\n',camera.get_T())

