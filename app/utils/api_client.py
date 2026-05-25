import os
import httpx
from typing import List, Dict, Tuple, Any, Optional
import streamlit as st

from app.utils.models import FieldOptimization, WellOptimization

class APIClient:
    """Client class handling exclusive HTTP communication with the FastAPI backend."""
    
    def __init__(self):
        # Allow overriding API URL from environment variables, defaulting to localhost:8000
        self.base_url = os.getenv("API_BASE_URL", "http://localhost:8000/api")
        self.timeout = 60.0  # Allow up to 60 seconds for complex optimizations

    def _handle_connection_error(self, e: Exception):
        """Standardized connection error renderer in Streamlit."""
        st.error("❌ **Unable to connect to the backend API server.**")
        st.info("💡 *Please ensure that the FastAPI server is running (e.g., `uvicorn backend.main:app --port 8000`) and accessible.*")
        st.exception(e)

    def get_wells(self) -> List[str]:
        """Fetch active wellbore names from the API."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(f"{self.base_url}/wells")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            self._handle_connection_error(e)
            return ["Well 1", "Well 2", "Well 3", "Well 4", "Well 5"]  # absolute minimum safe UI fallback

    def run_constrained_optimization(
        self, 
        q_gl_list: List[List[float]], 
        q_fluid_list: List[List[float]], 
        wct_list: List[float], 
        list_info: List[str], 
        settings: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], List[WellOptimization]]:
        """Trigger a constrained optimization run in the backend and return parsed results and well objects."""
        try:
            payload = {
                "q_gl_list": q_gl_list,
                "q_fluid_list": q_fluid_list,
                "wct_list": wct_list,
                "list_info": list_info,
                "qgl_limit": float(settings.get('qgl_limit_constrained', 4600.0)),
                "qgl_min": float(settings.get('qgl_min_constrained', 0.0)),
                "p_qoil": float(settings.get('p_qoil_constrained', 0.0)),
                "p_qgl": float(settings.get('p_qgl_constrained', 0.0))
            }
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(f"{self.base_url}/optimization/constrained", json=payload)
                response.raise_for_status()
                data = response.json()
                
                # Convert serialised well dicts back into active WellOptimization entities for frontend compatibility
                well_results = [WellOptimization.from_dict(w) for w in data.get("well_results", [])]
                return data.get("optimization_results", {}), well_results
        except Exception as e:
            self._handle_connection_error(e)
            raise e

    def run_global_optimization(
        self, 
        q_gl_list: List[List[float]], 
        q_fluid_list: List[List[float]], 
        wct_list: List[float], 
        list_info: List[str], 
        settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Trigger a global optimization run in the backend."""
        try:
            payload = {
                "q_gl_list": q_gl_list,
                "q_fluid_list": q_fluid_list,
                "wct_list": wct_list,
                "list_info": list_info,
                "qgl_min": float(settings.get('qgl_min_global', 0.0)),
                "p_qoil": float(settings.get('p_qoil_global', 0.0)),
                "p_qgl": float(settings.get('p_qgl_global', 0.0)),
                "max_iterations": int(settings.get('max_iterations', 40)),
                "max_qgl": int(settings.get('max_qgl', 50000))
            }
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(f"{self.base_url}/optimization/global", json=payload)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            self._handle_connection_error(e)
            raise e

    def get_optimization_history(self) -> List[FieldOptimization]:
        """Fetch historical field optimization runs from the backend database."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(f"{self.base_url}/optimization/history")
                response.raise_for_status()
                data = response.json()
                return [FieldOptimization.from_dict(opt) for opt in data]
        except Exception as e:
            self._handle_connection_error(e)
            return []

    def get_well_optimization_details(self, opt_id: int) -> List[WellOptimization]:
        """Fetch well optimization details for a specific historical run."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(f"{self.base_url}/optimization/history/{opt_id}/wells")
                response.raise_for_status()
                data = response.json()
                return [WellOptimization.from_dict(w) for w in data]
        except Exception as e:
            self._handle_connection_error(e)
            return []

    def get_latest_well_tests(self, well_names: List[str]) -> Any:
        """Fetch the latest production tests for the given wellbore names from the API."""
        try:
            payload = {"well_names": well_names}
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(f"{self.base_url}/wells/tests/latest", json=payload)
                response.raise_for_status()
                data = response.json()
                from app.utils.models import ProductionTest
                return [ProductionTest.from_dict(t) for t in data]
        except Exception as e:
            self._handle_connection_error(e)
            return []

    def load_data(self, file_bytes: bytes, filename: str) -> Tuple[List[List[float]], List[List[float]], List[float], List[str]]:
        """Upload production CSV bytes to the backend API and parse it on the server."""
        try:
            files = {"file": (filename, file_bytes, "text/csv")}
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(f"{self.base_url}/data/load", files=files)
                response.raise_for_status()
                data = response.json()
                return (
                    data.get("q_gl_list", []),
                    data.get("q_fluid_list", []),
                    data.get("wct_list", []),
                    data.get("list_info", [])
                )
        except Exception as e:
            self._handle_connection_error(e)
            return [], [], [], []


