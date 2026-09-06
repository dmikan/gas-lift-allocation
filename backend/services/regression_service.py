# services/regression_service.py
import numpy as np
from scipy.optimize import lsq_linear
from scipy import stats
from typing import Tuple, List, Union

class NamdarRegressor:
    """
    Fits well performance curve using Hamed Namdar's model:
    Q_o = a + b*Q_gl + c*Q_gl^0.7 + d*ln(Q_gl + 0.9) + e*exp(-Q_gl^0.6)
    Using bounded linear least squares (lsq_linear).
    Includes estimation of confidence (CI) and prediction (PI) intervals.
    """
    def __init__(self):
        self.beta = None
        self.S2 = None
        self.cov_free = None
        self.free_idx = None
        self.n_samples = 0
        self.p_params = 5
        self.is_fitted = False

    def _build_design_matrix(self, q_gl: np.ndarray) -> np.ndarray:
        """Construct the design matrix X for the given q_gl vector."""
        q_gl_clamped = np.maximum(q_gl, 1e-10)
        col_1 = np.ones_like(q_gl_clamped)
        col_qgl = q_gl_clamped
        col_pow = q_gl_clamped ** 0.7
        col_log = np.log(q_gl_clamped + 0.9)  # ln(q_gl + 0.9) as derived
        col_exp = np.exp(-(q_gl_clamped ** 0.6))
        return np.column_stack([col_1, col_qgl, col_pow, col_log, col_exp])

    def fit(self, q_gl: np.ndarray, y: np.ndarray, 
            bounds: Tuple[List[float], List[float]] = None) -> 'NamdarRegressor':
        """
        Fits the model using scipy.optimize.lsq_linear.
        
        Args:
            q_gl: Array of gas lift rates (independent variable)
            y: Array of production rates (dependent variable)
            bounds: Tuple of (lower_bounds, upper_bounds) for the 5 parameters
        """
        q_gl = np.asarray(q_gl, dtype=float)
        y = np.asarray(y, dtype=float)
        
        self.n_samples = len(q_gl)
        X = self._build_design_matrix(q_gl)
        
        if bounds is None:
            # Default bounds matching Trinidad / Namdar bounds in existing fitting_service
            lower_bounds = [-np.inf, -np.inf, 0.0, 0.0, 0.0]
            upper_bounds = [np.inf, 0.0, 200.0, 1000.0, 150.0]
            bounds = (lower_bounds, upper_bounds)
            
        # Run bounded linear least squares
        res = lsq_linear(X, y, bounds=bounds)
        self.beta = res.x
        
        # Calculate residual variance S^2 = RSS / (n - p)
        # res.fun is the residual vector: X * beta - y
        rss = np.sum(res.fun ** 2)
        df = self.n_samples - self.p_params
        
        if df > 0:
            self.S2 = rss / df
        else:
            self.S2 = 0.0
            
        # Active-set covariance calculation:
        # Determine free parameters (those not touching their bounds within a tolerance)
        lb, ub = bounds
        tol = 1e-7
        free_mask = []
        for i in range(self.p_params):
            val = self.beta[i]
            at_lower = (val - lb[i]) < tol if lb[i] is not None else False
            at_upper = (ub[i] - val) < tol if ub[i] is not None else False
            if at_lower or at_upper:
                free_mask.append(False)
            else:
                free_mask.append(True)
                
        self.free_idx = np.where(free_mask)[0]
        
        if len(self.free_idx) > 0 and df > 0:
            # Submatrix of X containing only columns of free parameters
            X_free = X[:, self.free_idx]
            try:
                # Compute covariance matrix (X_free^T * X_free)^-1
                self.cov_free = np.linalg.inv(X_free.T @ X_free)
            except np.linalg.LinAlgError:
                # Fallback to pseudo-inverse if singular
                self.cov_free = np.linalg.pinv(X_free.T @ X_free)
        else:
            self.cov_free = None
            
        self.is_fitted = True
        return self

    def predict(self, q_gl_pred: np.ndarray) -> np.ndarray:
        """Predict values for a given array of gas lift rates."""
        if not self.is_fitted:
            raise ValueError("Regressor is not fitted yet.")
        q_gl_pred = np.asarray(q_gl_pred, dtype=float)
        X_pred = self._build_design_matrix(q_gl_pred)
        return X_pred @ self.beta

    def predict_intervals(self, q_gl_pred: np.ndarray, alpha: float = 0.05) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculate 1-alpha confidence and prediction intervals.
        
        Returns:
            (ci_lower, ci_upper, pi_lower, pi_upper)
        """
        if not self.is_fitted:
            raise ValueError("Regressor is not fitted yet.")
            
        q_gl_pred = np.asarray(q_gl_pred, dtype=float)
        y_pred = self.predict(q_gl_pred)
        
        df = self.n_samples - self.p_params
        if df <= 0 or self.cov_free is None or self.S2 <= 0:
            # Fallback if intervals cannot be computed: return prediction
            return y_pred.copy(), y_pred.copy(), y_pred.copy(), y_pred.copy()
            
        X_pred = self._build_design_matrix(q_gl_pred)
        X_pred_free = X_pred[:, self.free_idx]
        
        # Calculate standard error of the mean:
        # SE_CI = sqrt( S2 * diag(X_pred_free * cov_free * X_pred_free^T) )
        # diag(A * B * A^T) = sum((A * B^T) * A, axis=1)
        var_mean = np.sum((X_pred_free @ self.cov_free) * X_pred_free, axis=1)
        var_mean = np.maximum(var_mean, 0.0) # Numerical guard
        se_ci = np.sqrt(self.S2 * var_mean)
        
        # Calculate standard error of the prediction:
        # SE_PI = sqrt( S2 * (1 + diag(X_pred_free * cov_free * X_pred_free^T)) )
        var_pred = 1.0 + var_mean
        se_pi = np.sqrt(self.S2 * var_pred)
        
        # Student's t critical value
        t_crit = stats.t.ppf(1.0 - alpha / 2.0, df=df)
        
        ci_lower = np.maximum(y_pred - t_crit * se_ci, 0.0)  # Rates cannot be negative
        ci_upper = y_pred + t_crit * se_ci
        
        pi_lower = np.maximum(y_pred - t_crit * se_pi, 0.0)
        pi_upper = y_pred + t_crit * se_pi
        
        return ci_lower, ci_upper, pi_lower, pi_upper
