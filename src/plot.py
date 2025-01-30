from camera import Camera
from point import Point

import cv2


class Plot:
    def __init__(self, camera):
        self.camera = camera

    def draw_tranform_coord(self, points):
        prew_point = self.camera.direct_transform(points[0])
        prew_point_plot = tuple(map(int, prew_point.get_image()[:2]))
        for point in points[1:]:
            new_point = self.camera.direct_transform(point)
            new_point_plot = tuple(map(int, new_point.get_image()[:2]))
            cv2.line(self.camera.get_scene(), prew_point_plot,
                     new_point_plot, (0, 255, 0), 2)
            prew_point = new_point
        cv2.imshow('Вид сцены калибровочный', self.camera.get_scene())
        cv2.waitKey(0)
        cv2.destroyAllWindows()

