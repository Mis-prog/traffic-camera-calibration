from core.camera import Camera
from calibration.base import Calibration


class CalibrationPipeline:
    def __init__(self,
                 init_stage: Calibration = None,
                 refine_stage: Calibration = None):
        """
        :param init_stage: этап начальной калибровки  по точкам схода
        :param refine_stage: этап уточнения (например, прямая/обратная оптимизация)
        """
        self.init_stage = init_stage
        self.refine_stage = refine_stage

    def run(self, camera: Camera, lines: dict, **kwargs) -> Camera:
        """
        Выполняет последовательную калибровку камеры.

        :param camera: объект камеры
        :param lines: данные разметки (напр. {'angle': [...], 'parallel-1': [...]})
        :param kwargs: дополнительные аргументы (например, error_func или solver)
        """

        if self.init_stage:
            print("[INFO] Initial calibration...")
            self.init_stage.camera = camera
            camera = self.init_stage.run(lines)

        if self.refine_stage:
            print("[INFO] Refinement calibration...")
            self.refine_stage.camera = camera
            camera = self.refine_stage.run(lines)

        return camera
