from core.camera import Camera


class Calibration:
    def run(self, camera, **kwargs):
        raise NotImplementedError("Must be implemented in subclass.")
