import os
import sys
import numpy as np

# Ensure backend is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.services.fitting_service import FittingService

def test_fitting_service_wct():
    # Synthetic data for 2 wells
    q_gl_list = [np.array([50, 100, 200], dtype=float), np.array([60, 120, 240], dtype=float)]
    q_fluid_list = [np.array([100, 150, 200], dtype=float), np.array([120, 180, 240], dtype=float)]
    wct_list = [0.15, 0.30]
    
    service = FittingService(q_gl_list, q_fluid_list, wct_list)
    results = service.perform_fitting_group()
    
    assert "plot_data" in results
    assert len(results["plot_data"]) == 2
    
    # Check that wct is present in plot_data
    assert results["plot_data"][0]["wct"] == 0.15
    assert results["plot_data"][1]["wct"] == 0.30
    
    print("✅ FittingService wct test passed!")

if __name__ == "__main__":
    test_fitting_service_wct()
