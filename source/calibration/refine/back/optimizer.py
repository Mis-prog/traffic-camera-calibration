import numpy as np
from scipy.optimize import least_squares

from calibration.base import Calibration
from core.camera import Camera
from core.pointND import PointND
from .error_funk import compute_total_residuals


class BackProjectionOptimizer(Calibration):
    def __init__(self, camera: Camera, debug_save_path: str = None):
        super().__init__(camera, debug_save_path)

    def run(self, data, **kwargs) -> Camera:
        """
        :param data: ограничения
        :return: обновлённая камера
        """

        residual_blocks = kwargs.get("resuals_blocks", None)
        print("=" * 50)
        print("🔧 [BackProjectionOptimizer] Запуск дооптимизации параметров камеры")
        print("=" * 50)

        init_params = self.camera.get_params()
        print(f"📌 Начальные параметры: {np.round(init_params, 4)}")

        res_fn = lambda p: compute_total_residuals(self.camera, data, p, residual_blocks)

        result = least_squares(res_fn, init_params, verbose=2)

        print("-" * 50)
        print(f"✅ Оптимизация завершена")
        print(f"🔁 Итераций: {result.nfev}")
        print(f"🎯 Финальная ошибка (cost): {result.cost:.6f}")
        print(f"📍 Обновлённые параметры: {np.round(result.x, 4)}")
        self.camera.set_params_from_list(result.x)
