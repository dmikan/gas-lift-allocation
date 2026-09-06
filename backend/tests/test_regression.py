# tests/test_regression.py
import os
import sys
import numpy as np

# Ensure backend is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.services.regression_service import NamdarRegressor

def test_regression_fitting():
    print("Testing NamdarRegressor fitting...")
    # Generate synthetic data
    np.random.seed(42)
    q_gl = np.array([50, 100, 200, 400, 600, 800, 1000, 1200, 1500, 1800, 2000], dtype=float)
    
    # Namdar model parameters: a=100, b=-0.05, c=15, d=50, e=20
    # Formula: a + b*q + c*q^0.7 + d*ln(q + 0.9) + e*exp(-q^0.6)
    a_true, b_true, c_true, d_true, e_true = 120.0, -0.05, 10.0, 40.0, 30.0
    
    # Calculate noise-free y
    y_true = (a_true + 
              b_true * q_gl + 
              c_true * (q_gl ** 0.7) + 
              d_true * np.log(q_gl + 0.9) + 
              e_true * np.exp(-(q_gl ** 0.6)))
    
    # Add Gaussian noise
    noise = np.random.normal(0, 5.0, size=len(q_gl))
    y_noisy = y_true + noise
    
    # Fit the regressor
    regressor = NamdarRegressor()
    bounds = (
        [-np.inf, -np.inf, 0.0, 0.0, 0.0],
        [np.inf, 0.0, 200.0, 1000.0, 150.0]
    )
    regressor.fit(q_gl, y_noisy, bounds=bounds)
    
    assert regressor.is_fitted
    assert len(regressor.beta) == 5
    print(f"✅ Fitted coefficients: {regressor.beta}")
    
    # Predict and calculate intervals
    q_gl_pred = np.linspace(10, 2100, 100)
    y_pred = regressor.predict(q_gl_pred)
    ci_lower, ci_upper, pi_lower, pi_upper = regressor.predict_intervals(q_gl_pred, alpha=0.05)
    
    # Assert basic inequalities
    assert np.all(ci_upper >= ci_lower), "Confidence interval upper bound should be >= lower bound"
    assert np.all(pi_upper >= pi_lower), "Prediction interval upper bound should be >= lower bound"
    
    # PI should be strictly wider than CI
    ci_width = ci_upper - ci_lower
    pi_width = pi_upper - pi_lower
    assert np.all(pi_width > ci_width), "Prediction Interval must be wider than Confidence Interval"
    
    # Physically, rates cannot be negative
    assert np.all(ci_lower >= 0.0), "CI lower bounds should be non-negative"
    assert np.all(pi_lower >= 0.0), "PI lower bounds should be non-negative"
    
    print("✅ All basic regression and interval assertions passed.")

def test_regression_edge_cases():
    print("Testing edge cases (small sample size n <= 5)...")
    regressor = NamdarRegressor()
    
    # n = 4 (less than 5 parameters)
    q_gl_small = np.array([100, 200, 300, 400], dtype=float)
    y_small = np.array([50, 120, 180, 200], dtype=float)
    
    try:
        regressor.fit(q_gl_small, y_small)
        assert regressor.is_fitted
        print("✅ Fit completed for n <= 5.")
        
        # Test that predict_intervals doesn't fail but handles it gracefully
        ci_lower, ci_upper, pi_lower, pi_upper = regressor.predict_intervals(q_gl_small)
        # For small n, it falls back to return the predictions themselves
        y_pred = regressor.predict(q_gl_small)
        assert np.allclose(ci_lower, y_pred), "CI lower bound should fall back to y_pred"
        assert np.allclose(pi_upper, y_pred), "PI upper bound should fall back to y_pred"
        print("✅ Graceful fallback verified for n <= 5.")
    except Exception as e:
        assert False, f"Regression raised exception on small n: {e}"

def test_active_constraints():
    print("Testing active constraints handling...")
    # Force a parameter to hit the bounds
    # Trinidad bounds: lower_bounds = [-np.inf, -np.inf, 0, 0, 0]
    # If we fit a y vector that decreases very sharply, 'b' (linear term) will hit its upper limit (0.0),
    # or some terms will hit 0.0. Let's see if active constraints are handled correctly.
    np.random.seed(42)
    q_gl = np.array([50, 100, 200, 400, 600, 800, 1000], dtype=float)
    # Target value that goes to zero immediately (impossible to fit Namdar without hitting borders)
    y = np.array([10, 5, 2, 1, 0, 0, 0], dtype=float)
    
    regressor = NamdarRegressor()
    bounds = (
        [-np.inf, -np.inf, 0.0, 0.0, 0.0],
        [np.inf, 0.0, 200.0, 1000.0, 150.0]
    )
    regressor.fit(q_gl, y, bounds=bounds)
    
    assert regressor.is_fitted
    print(f"✅ Fitted coefficients under constraints: {regressor.beta}")
    print(f"✅ Free variables index: {regressor.free_idx}")
    
    # Ensure it calculates intervals without failing
    ci_lower, ci_upper, pi_lower, pi_upper = regressor.predict_intervals(q_gl)
    assert np.all(ci_upper >= ci_lower)
    print("✅ Active constraints regression test completed.")

if __name__ == "__main__":
    test_regression_fitting()
    test_regression_edge_cases()
    test_active_constraints()
    print("🎉 All regression tests passed successfully!")
