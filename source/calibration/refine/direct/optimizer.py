import numpy as np
from scipy.optimize import least_squares

from calibration.base import Calibration
from core.camera import Camera
from core.pointND import PointND
from .error_funk import target_residuals_lsq


class DirectProjectionOptimizer(Calibration):
    def __init__(self, camera: Camera, debug_save_path: str = None):
        super().__init__(camera, debug_save_path)

    def run(self, data, **kwargs) -> Camera:
        """
        :param data
        :return: обновлённая камера
        """
        print("[Direct] Start refine ...")

        residual_blocks = kwargs.get("resuals_blocks")
        x0 = kwargs.get("x0", self.camera.get_params())
        solver = kwargs.get("solver", least_squares)
        method = kwargs.get("method", "trf")
        bounds = kwargs.get("bounds", ([900, -360, -360, -360, -30, -30, 5], [2000, 360, 360, 360, 30, 30, 30]))
        mask = kwargs.get("mask", [0, 1, 2, 3, 4, 5, 6])

        print("=" * 50)
        print("🔧 [DirectProjectionOptimizer] Запуск дооптимизации параметров камеры")
        print("=" * 50)

        print(f"📌 Начальные параметры: {np.round(x0, 2).tolist()}")

        full_params = np.array(self.camera.get_params(), dtype=float)
        x0 = full_params[mask]

        def loss_fn(masked_params):
            current_params = full_params.copy()
            current_params[mask] = masked_params
            return self.compute_total_residuals(self.camera, data, current_params, residual_blocks)

        result = solver(loss_fn, x0,
                        method=method,
                        bounds=bounds,
                        verbose=2,
                        loss='soft_l1'
                        )

        print("-" * 50)
        print(f"✅ Оптимизация завершена")
        print(f"🔁 Итераций: {result.nfev}")
        print(f"🎯 Финальная ошибка (cost): {result.cost:.6f}")
        print("📍 Обновлённые параметры:", np.round(result.x, 2).tolist())
        full_params[mask] = result.x

        self.camera.set_params_from_list(full_params)

        if self.debug_save_path is not None:
            from calibration.debug import visualize_grid_debug
            point_start = PointND(self.camera.intrinsics.get_main_point(), add_weight=True)
            visualize_grid_debug(self.camera, point_start, save_path=self.debug_save_path + "grid.png")

        return self.camera
