from source.core.camera import Camera
from .base import Calibration


class CalibrationPipeline:
    def __init__(self, init_stage=None, refine_stages: list = None, n_iter: int = 1):
        """
        :param init_stage: начальная калибровка (обычно по точкам схода)
        :param refine_stages: список уточняющих оптимизаторов (по координатам и т.п.)
        :param n_iter: количество итераций уточняющих этапов
        """
        self.init_stage = init_stage
        self.refine_stages = refine_stages or []
        self.n_iter = n_iter

    def run(self, camera: Camera, data: dict, **kwargs) -> Camera:
        """
        Запуск начального этапа и итераций уточняющих оптимизаций.

        :param camera: объект Camera
        :param data: словарь с разметкой
        :param kwargs: дополнительные параметры
        :return: откалиброванная камера
        """
        if self.init_stage:
            print(f"🚀 [Pipeline] Начальный этап: {self.init_stage.__class__.__name__}")
            self.init_stage.camera = camera
            camera = self.init_stage.run(data, **kwargs)
            print("✅ [Pipeline] Начальная калибровка завершена\n")

        for iteration in range(1, self.n_iter + 1):
            print(f"🔁 [Pipeline] Итерация уточнения {iteration}/{self.n_iter}")

            for idx, stage in enumerate(self.refine_stages, 1):
                stage.camera = camera
                print(f"🔧 [Pipeline] Этап {idx}: {stage.__class__.__name__}")
                camera = stage.run(data, **kwargs)
                print(f"✅ [Pipeline] Этап {idx} завершён\n")

        print("🎯 [Pipeline] Калибровка завершена")
        print("=" * 60)
        print(f"[Pipeline] Конечные значения {[round(float(p), 2) for p in camera.get_params()]}")
        return camera
