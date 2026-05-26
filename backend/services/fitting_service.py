# services/fitting_service.py
import numpy as np
from typing import List, Dict, Tuple, TypedDict
from scipy import optimize

class FittingService:
    """Service that handles all curve fitting operations and performance curve modeling"""
    def __init__(self, q_gl_list: List[np.ndarray], q_fluid_list: List[np.ndarray], wct_list: List[float]):
        """
        Initialize with well data

        Args:
            q_gl_list: List of arrays containing gas lift rates for each well
            q_fluid_list: List of arrays containing oil production rates for each well
        """
        self.q_gl_list = q_gl_list
        self.q_fluid_list = q_fluid_list
        self.wct_list = wct_list
        self.q_gl_common_range = None
        self.y_pred_fluid_list = None
        self.plot_data = None

    def _calculate_qgl_range(self) -> np.ndarray:
        q_gl_max = max([np.max(j) for j in self.q_gl_list])
        return np.logspace(0.1, np.log10(q_gl_max), 1000)


    def _prepare_well_data(self, q_gl: List[float], q_fluid: List[float]) -> Tuple[np.ndarray, np.ndarray]:
        q_gl = np.array(q_gl, dtype=float)
        q_fluid = np.array(q_fluid, dtype=float)
        valid_mask = ~(np.isnan(q_gl) | np.isnan(q_fluid) |
                     np.isinf(q_gl) | np.isinf(q_fluid))
        q_gl = q_gl[valid_mask]
        q_fluid = q_fluid[valid_mask]
        return np.maximum(q_gl, 1e-10), q_fluid

    def _nishikiori_parameters(self):
        """Return default parameters for Nishikiori model"""
        p0 = [100, 0.1, 100, 100, 50]
        bounds = (
            [-np.inf, -np.inf, 0, -1000, 0],
            [np.inf, np.inf, 200, 1000, 150]
        )
        return p0, bounds

    def _trinidad_parameters(self):
        """Return default parameters for Trinidad model"""
        p0 = [100, -0.1, 100, 100, 50]
        bounds = (
            [-np.inf, -np.inf, 0, 0, 0],
            [np.inf, 0, 200, 1000, 150]
        )
        return p0, bounds

    def _fit_model(self, q_gl: np.ndarray, q_fluid: np.ndarray) -> np.ndarray:
        """Internal method to fit a single well's data"""
        try:
            p0, bounds = self._trinidad_parameters()
            params_list, _ = optimize.curve_fit(
                self._model_namdar,
                q_gl,
                q_fluid,
                p0=p0,
                bounds=bounds,
                maxfev=500000
            )

            print("✅ Parameters adjusted:", [f"{param:.2f}" for param in params_list])
            y_pred = self._model_namdar(self.q_gl_common_range, *params_list)
            return np.maximum(y_pred, 0)
        except Exception as e:
            print(f"❌ Error in the adjustment: {str(e)}")
            return np.zeros_like(self.q_gl_common_range) + np.mean(q_fluid)


    def _model_namdar(self, q_gl_common_range: np.ndarray, a: float, b: float, c: float,
                    d: float, e: float) -> np.ndarray:
        q_gl_common_range = np.maximum(q_gl_common_range, 1e-10)
        return (
            a + b * q_gl_common_range + c * (q_gl_common_range ** 0.7) +
            d * np.log(q_gl_common_range) + e * np.exp(-(q_gl_common_range ** 0.6)))


    def _model_dan(self, q_gl_common_range: np.ndarray, a: float, b: float, c: float,
                d: float, e: float) -> np.ndarray:
        q_gl_common_range = np.maximum(q_gl_common_range, 1e-10)
        return (
            a + b * q_gl_common_range + c * (q_gl_common_range ** 0.5) +
            d * np.log(q_gl_common_range) + e * np.exp(-q_gl_common_range))

    def perform_fitting_group(self) -> Dict:
        """
        Perform curve fitting for all wells

        Returns:
            Dictionary containing:
            - qgl_range: Generated gas lift range
            - y_pred_list: Predicted fluid rates for each well
            - plot_data: Visualization-ready data for each well
            - oil_rates: Calculated oil rates per well
        """
        self.q_gl_common_range = self._calculate_qgl_range()
        self.y_pred_fluid_list = []
        self.plot_data = []

        for well_num, (q_gl, q_fluid) in enumerate(zip(self.q_gl_list, self.q_fluid_list)):

            # Prepare, clean data and perform fitting
            q_gl_clean, q_fluid_clean = self._prepare_well_data(q_gl, q_fluid)
            y_pred_fluid = self._fit_model(q_gl_clean, q_fluid_clean)
            self.y_pred_fluid_list.append(y_pred_fluid)

            # Store plot data
            self.plot_data.append({
                "well_num": well_num + 1,
                "q_gl_original": q_gl_clean,
                "q_fluid_original": q_fluid_clean,
                "q_gl_common_range": self.q_gl_common_range,
                "q_fluid_predicted": y_pred_fluid,
                "q_oil_predicted": y_pred_fluid * (1 - self.wct_list[well_num])
            })

        return {
            "q_gl_common_range": self.q_gl_common_range,
            "y_pred_fluid_list": self.y_pred_fluid_list,
            "q_oil_rates_list": self._calculate_oil_rates(),
            "plot_data": self.plot_data
        }

    def _calculate_oil_rates(self) -> List[List[float]]:
        oil_rates_list = []
        for fluid_rates_well, wct in zip(self.y_pred_fluid_list, self.wct_list):
            oil_rates_well = [fluid_rate * (1 - wct) for fluid_rate in fluid_rates_well]
            oil_rates_list.append(oil_rates_well)
        return oil_rates_list