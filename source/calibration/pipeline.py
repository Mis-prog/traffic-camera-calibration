from core.camera import Camera
from calibration.base import Calibration


class CalibrationPipeline:
    def __init__(self, stages: list[Calibration]):
        """
        :param init_stage: этап начальной калибровки  по точкам схода
        :param refine_stage: этап уточнения (например, прямая/обратная оптимизация)
        """
        self.stages = stages

    def run(self, camera: Camera, data: dict, **kwargs) -> Camera:
        """
        Выполняет последовательную калибровку камеры.

        :param camera: объект камеры
        :param data: данные разметки (напр. {'angle': [...], 'parallel-1': [...]})
        :param kwargs: дополнительные аргументы (например, error_func или solver)
        """

        for idx, stage in enumerate(self.stages, 1):
            stage.camera = camera
            print("=" * 60)
            print(f"🔧 [Pipeline] Этап {idx}: {stage.__class__.__name__}")
            print("=" * 60)
            camera = stage.run(data, **kwargs)
            print(f"✅ [Pipeline] Этап {idx} завершён\n")

        print("🎯 [Pipeline] Калибровка камеры завершена")
        print("=" * 60)
        print(f" [Pipeline] Конечные значения {[round(float(p), 2) for p in camera.get_params()]}")

        return camera
