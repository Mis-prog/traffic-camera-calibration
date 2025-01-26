from camera import Camera
from optimizetion import Optimizer
from initsolution import calc_init_camera
from point import Point


# Линии схода относительно направлений
Line_Y = [[[786, 689], [281, 515]], [[1061, 516], [213, 340]], [[1008, 421], [375, 311]], [[355, 264], [70, 238]], [[362, 223], [73, 211]]]
Line_X = [[[300, 513], [555, 185]], [[835, 677], [927, 264]], [[674, 117], [740, 13]], [[833, 192], [842, 158]], [[954, 142], [954, 38]]]

camera = calc_init_camera('../data/scene_from_crossroads_not_dist.png',[Line_X, Line_Y])

# camera.get_R(angle_output=True,output=True)

# Калибровочные линии
lines = [
    [[831, 689, 1 , 7.71, 0, 0, 1], 
    [299, 520, 1, 7.71, 20.7, 0 , 1]],
    [[1007, 425, 1, 18.9, 0, 0, 1],
    [439, 322, 1,18.9, 20.7, 0, 1]],
    [[927, 267, 1, 31.9, 0, 0, 1],
    [553, 189, 1, 31.9, 20.7, 0, 1]]
]

lines_point = []
for line in lines:
    start_point, end_point = line 
    start_point = Point.from_combined(start_point)
    end_point = Point.from_combined(end_point)
    lines_point.append([start_point,end_point])
    

optimize = Optimizer(camera)

result = optimize.optimize(lines_point)
print(result)