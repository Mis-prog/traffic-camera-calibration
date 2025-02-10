import cv2
import matplotlib.pyplot as plt

from .camera_model import Camera
from .point2D import Point2D
from .point3D import Point3D


class Plot:
    def __init__(self, camera):
        self.camera = camera
        self.scene_plot = self.camera.get_scene().copy()

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

    def _get_cv2_format(self, point: Point2D):
        return tuple(map(int, point.get()))

    def draw_tranform_line(self, lines, save=False, out_jupyter=False, params=[]):
        scene = self.camera.get_scene().copy()

        overlay = scene.copy()
        for start, end in lines:
            start_trans = self.camera.direct_transform_world(start[1], params)
            end_trans = self.camera.direct_transform_world(end[1], params)

            start_plot = self._get_cv2_format(start_trans)
            self._draw_point_with_label(overlay, start_plot, start[1].get())
            end_plot = self._get_cv2_format(end_trans)
            self._draw_point_with_label(overlay, end_plot, end[1].get())

            cv2.line(overlay, start_plot,
                     end_plot, (0, 255, 0), 2)

        alpha = 0.8
        cv2.addWeighted(overlay, alpha, scene, 1 - alpha, 0, scene)

        if not save and not out_jupyter:
            cv2.imshow('Вид сцены калибровочный', scene)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        elif out_jupyter:
            scene_rgb = cv2.cvtColor(scene, cv2.COLOR_BGR2RGB)
            plt.figure(figsize=(10, 8))
            plt.imshow(scene_rgb)
            plt.axis('off')
            plt.show()
        else:
            cv2.imwrite('../data/evalution_scene.png', scene)

    def draw_transform_point(self, points, save=False, out_jupyter=False, params=[]):
        scene = self.camera.get_scene().copy()

        overlay = scene.copy()
        for point in points:
            point_trans = self.camera.direct_transform_world(point, params)

            start_plot = self._get_cv2_format(point_trans)
            self._draw_point_with_label(overlay, start_plot, point_trans.get())


        alpha = 0.8
        cv2.addWeighted(overlay, alpha, scene, 1 - alpha, 0, scene)

        if not save and not out_jupyter:
            cv2.imshow('Вид сцены калибровочный', scene)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        elif out_jupyter:
            scene_rgb = cv2.cvtColor(scene, cv2.COLOR_BGR2RGB)
            plt.figure(figsize=(10, 8))
            plt.imshow(scene_rgb)
            plt.axis('off')
            plt.show()
        else:
            cv2.imwrite('../data/evalution_scene.png', scene)

    def draw_calibration_line(self, lines: list[tuple[tuple[Point2D, Point3D], tuple[Point2D, Point3D]]], save=False,
                              out_jupyter=False):
        scene = self.camera.get_scene()

        for start, end in lines:
            start_plot = self._get_cv2_format(start[0])
            end_plot = self._get_cv2_format(end[0])
            self._draw_point_with_label(scene, start_plot, start[1].get())
            self._draw_point_with_label(scene, end_plot, end[1].get())
            cv2.line(scene, start_plot,
                     end_plot, (0, 255, 0), 2)

        if not save and not out_jupyter:
            cv2.imshow('Вид сцены калибровочный', self.camera.get_scene())
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        elif out_jupyter:
            scene_rgb = cv2.cvtColor(scene, cv2.COLOR_BGR2RGB)
            plt.figure(figsize=(10, 8))
            plt.imshow(scene_rgb)
            plt.axis('off')
            plt.show()
        else:
            cv2.imwrite('../data/calibration_line.png', scene)
