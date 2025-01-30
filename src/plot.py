from camera import Camera
from point import Point

import cv2


class Plot:
    def __init__(self, camera):
        self.camera = camera

        cv2.line(self.camera.get_scene(), (828, 689), (927, 262), (0, 0, 0), 2)
        cv2.line(self.camera.get_scene(), (828, 700), (290, 513), (0, 0, 0), 2)
        cv2.putText(self.camera.get_scene(), 'OX', (927, 262), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(self.camera.get_scene(), 'OY', (290, 513), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)

    def _draw_point_with_label(self, img, point, coords):
        cv2.circle(img, point, 5, (0, 0, 255), -1)
        if len(coords) == 2:
            text = f"({coords[0]:.1f}, {coords[1]:.1f})"
        else:
            text = f"({coords[0]:.1f}, {coords[1]:.1f}, {coords[2]:.1f} )"
        cv2.putText(img, text, (point[0] + 5, point[1] - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    def _get_cv2_format(self, point: Point):
        return tuple(map(int, point.get_image()[:2]))

    def draw_tranform_coord(self, points, save=False):
        scene = self.camera.get_scene()

        prew_point = self.camera.direct_transform(points[0])
        prew_point_plot = self._get_cv2_format(prew_point)
        self._draw_point_with_label(scene, prew_point_plot, prew_point.get_real())
        for point in points[1:]:
            new_point = self.camera.direct_transform(point)
            new_point_plot = self._get_cv2_format(new_point)

            self._draw_point_with_label(scene, new_point_plot, new_point.get_real())
            cv2.line(scene, prew_point_plot,
                     new_point_plot, (0, 255, 0), 2)
            prew_point_plot = new_point_plot

        if not save:
            cv2.imshow('Вид сцены калибровочный', self.camera.get_scene())
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            cv2.imwrite('../data/evalution_scene.png', scene)

    def draw_calibration_line(self, line,save=False):
        scene = self.camera.get_scene()

        for start, end in line:
            start_plot = self._get_cv2_format(start)
            end_plot = self._get_cv2_format(end)
            self._draw_point_with_label(scene, start_plot,start.get_real())
            self._draw_point_with_label(scene, end_plot,end.get_real())
            cv2.line(scene, start_plot,
                     end_plot, (0, 255, 0), 2)

        if not save:
            cv2.imshow('Вид сцены калибровочный', self.camera.get_scene())
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            cv2.imwrite('../data/calibration_line.png', scene)