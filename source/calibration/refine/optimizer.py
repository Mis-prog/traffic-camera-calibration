import numpy as np
from pandas.core.methods.selectn import SelectNSeries
from scipy.optimize import least_squares, minimize

from source.calibration.base import Calibration
from source.core.camera import Camera
from source.core.pointND import PointND


class RefineOptimizer(Calibration):
    def __init__(self, camera: Camera,
                 residual_blocks: list,
                 bounds: tuple = None,
                 solver=least_squares,
                 method: str = "trf",
                 mask: list = None,
                 debug_save_path: str = None,
                 gps_origin: tuple = None,
                 ):
        super().__init__(camera, debug_save_path)
        self.residual_blocks = residual_blocks
        self.bounds = bounds if bounds is not None else ([800, -360, -360, -360, -30, -30, 5],
                                                         [2000, 360, 360, 360, 30, 30, 30])
        self.mask = mask if mask is not None else [0, 1, 2, 3, 4, 5, 6]
        self.solver = solver
        self.method = method
        self.gps_origin = gps_origin

    def run(self, data, **kwargs) -> Camera:
        """
        :param data: ограничения
        :return: обновлённая камера
        """

        print("=" * 50)
        print("🔧 [RefineOptimizer] Запуск дооптимизации параметров камеры")
        print("=" * 50)

        full_params = np.array(self.camera.get_params(), dtype=float)
        print(f"📌 Начальные параметры: {np.round(full_params, 2).tolist()}")

        x0 = full_params[self.mask]

        def loss_fn(masked_params):
            current_params = full_params.copy()
            current_params[self.mask] = masked_params
            return self.compute_total_residuals(self.camera, data, current_params, self.residual_blocks)

        def loss_fn_mse(masked_params):
            current_params = full_params.copy()
            current_params[self.mask] = masked_params
            return self.compute_total_mse(self.camera, data, current_params, self.residual_blocks)

        if self.method == "lm":
            result = self.solver(loss_fn,
                                 x0,
                                 method=self.method,
                                 # verbose=2,
                                 max_nfev=10000
                                 )
        elif self.method == "trf":
            result = self.solver(loss_fn,
                                 x0,
                                 method=self.method,
                                 bounds=self.bounds,
                                 # verbose=2,
                                 max_nfev=3000,
                                 gtol=1e-8,
                                 xtol=1e-8,
                                 ftol=1e-8
                                 )
        elif self.method == "minimize":
            result = minimize(
                fun=loss_fn_mse,
                x0=x0,
                bounds=self.bounds,
                method='Powell'
            )

        print("-" * 50)
        print(f"✅ Оптимизация завершена")
        print(f"🔁 Итераций: {result.nfev}")
        if self.method in ["trf","lm"]:
            print(f"🎯 Финальная ошибка (cost): {result.cost:.6f}")
        else:
            print(f"🎯 Финальная ошибка (cost): {result.fun:.6f}")
        print("📍 Обновлённые параметры:", np.round(result.x, 2).tolist())
        full_params[self.mask] = result.x

        self.camera.set_params_from_list(full_params)

        if self.debug_save_path is not None:
            from source.calibration.debug import visualize_grid_debug, visualize_grid_gps_debug
            point_start = PointND(self.camera.intrinsics.get_main_point(), add_weight=True)
            visualize_grid_debug(self.camera, point_start, save_path=self.debug_save_path, grid_range=12,
                                 grid_step=1)
            # visualize_grid_gps_debug(self.camera, point_start, gps_origin=self.gps_origin)
            if self.gps_origin is not None:
                pass

        return self.camera
