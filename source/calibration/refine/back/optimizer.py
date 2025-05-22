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

        residual_blocks = kwargs.get("resuals_blocks")
        x0 = kwargs.get("x0", self.camera.get_params())
        solver = kwargs.get("solver", least_squares)
        method = kwargs.get("method", "trf")
        bounds = kwargs.get("bounds", ([900, -30, -30, 5], [2000, 30, 30, 30]))

        print("=" * 50)
        print("🔧 [BackProjectionOptimizer] Запуск дооптимизации параметров камеры")
        print("=" * 50)

        print(f"📌 Начальные параметры: {np.round(x0, 2).tolist()}")

        # res_fn = lambda p: compute_total_residuals(self.camera, data, p, residual_blocks)

        full_params = np.array(self.camera.get_params(), dtype=float)
        mask_indices = [0, 4, 5, 6]
        x0 = full_params[mask_indices]

        def loss_fn(masked_params):
            current_params = full_params.copy()
            current_params[mask_indices] = masked_params
            return compute_total_residuals(self.camera, data, current_params, residual_blocks)

        result = solver(loss_fn, x0,
                        method=method,
                        bounds=bounds,
                        verbose=2,
                        loss='linear'
                        )

        print("-" * 50)
        print(f"✅ Оптимизация завершена")
        print(f"🔁 Итераций: {result.nfev}")
        print(f"🎯 Финальная ошибка (cost): {result.cost:.6f}")
        print("📍 Обновлённые параметры:", np.round(result.x, 2).tolist())
        full_params[mask_indices] = result.x

        self.camera.set_params_from_list(full_params)

        if self.debug_save_path is not None:
            from calibration.debug import visualize_grid_debug, visualize_coordinate_system
            point_start = PointND(self.camera.intrinsics.get_main_point(), add_weight=True)
            visualize_grid_debug(self.camera, point_start, save_path=self.debug_save_path + "grid.png")

        return self.camera
