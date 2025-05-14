import cv2

from camera_intrinsics import CameraIntrinsics
from camera_extrinsics import CameraExtrinsics
from pointND import PointND


class Camera:
    def __init__(self, path_image):
        image = cv2.imread(path_image)
        self.size = image.shape[:2]
        self.path = path_image

        self.intrinsics = CameraIntrinsics(self.size[1], self.size[0])
        self.extrinsics = CameraExtrinsics()

    def set_params(self, params):
        pass

    def project_direct(self, point3D: PointND) -> PointND:
        pass

    def project_back(self, point2D: PointND) -> PointND:
        pass

    def homography(self, point: PointND, direction='direct') -> PointND:
        pass