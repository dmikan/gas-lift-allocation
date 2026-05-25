from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List, Dict, Any, Optional
import numpy as np

from backend.database import get_db_session
from backend.entities.field_optimization import FieldOptimization
from backend.entities.well_optimization import WellOptimization
from backend.repositories.field_optimization_repository import FieldOptimizationRepository
from backend.repositories.well_optimization_repository import WellOptimizationRepository
from backend.services.field_optimization_service import FieldOptimizationService
from backend.services.well_optimization_service import WellOptimizationService
from backend.services.fitting_service import FittingService
from backend.services.optimization_constrained_pipeline_service import OptimizationConstrainedPipelineService
from backend.services.optimization_global_pipeline_service import OptimizationGlobalPipelineService

from pydantic import BaseModel

router = APIRouter(prefix="/optimization", tags=["Optimization"])

# --- Pydantic Models for Input Validation ---
class ConstrainedOptimizationRequest(BaseModel):
    q_gl_list: List[List[float]]
    q_fluid_list: List[List[float]]
    wct_list: List[float]
    list_info: List[str]
    qgl_limit: float = 4600.0
    qgl_min: float = 0.0
    p_qoil: float = 0.0
    p_qgl: float = 0.0

class GlobalOptimizationRequest(BaseModel):
    q_gl_list: List[List[float]]
    q_fluid_list: List[List[float]]
    wct_list: List[float]
    list_info: List[str]
    qgl_min: float = 0.0
    p_qoil: float = 0.0
    p_qgl: float = 0.0
    max_iterations: int = 40
    max_qgl: int = 50000

# --- Helper Function for JSON Serialization ---
def clean_numpy_and_nans(obj: Any) -> Any:
    """Recursively convert numpy arrays, integers, floats and NaNs to serializable Python objects."""
    if isinstance(obj, dict):
        return {k: clean_numpy_and_nans(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_numpy_and_nans(v) for v in obj]
    elif isinstance(obj, tuple):
        return tuple(clean_numpy_and_nans(v) for v in obj)
    elif isinstance(obj, np.ndarray):
        return clean_numpy_and_nans(obj.tolist())
    elif isinstance(obj, (np.floating, float)):
        return None if np.isnan(obj) else float(obj)
    elif isinstance(obj, (np.integer, int)):
        return int(obj)
    return obj


# --- API Routes ---

@router.post("/constrained")
def run_constrained_optimization(
    req: ConstrainedOptimizationRequest, 
    session: Session = Depends(get_db_session)
):
    """Execute constrained optimization and persist results using SQLModel ORM."""
    try:
        # Step 1: Perform curve fitting
        fitting_service = FittingService(req.q_gl_list, req.q_fluid_list, req.wct_list)
        fit = fitting_service.perform_fitting_group()

        # Step 2: Initialize and run optimization pipeline
        pipeline = OptimizationConstrainedPipelineService(
            q_gl_common_range=fit['q_gl_common_range'],
            q_oil_rates_list=fit["q_oil_rates_list"],
            plot_data=fit["plot_data"],
            list_info=req.list_info,
            qgl_limit=req.qgl_limit,
            qgl_min=req.qgl_min,
            p_qoil=req.p_qoil,
            p_qgl=req.p_qgl,
            db=session
        )
        optimization_results = pipeline.run()

        # Step 3: Fetch the newly saved well results
        well_repo = WellOptimizationRepository(session)
        well_service = WellOptimizationService(well_repo)
        well_results = well_service.get_latest_well_optimizations()

        # Clean all numpy objects and serialise safely
        response_data = {
            "optimization_results": clean_numpy_and_nans(optimization_results),
            "well_results": [clean_numpy_and_nans(w.to_dict()) for w in well_results]
        }
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Constrained optimization failed: {str(e)}")


@router.post("/global")
def run_global_optimization(
    req: GlobalOptimizationRequest
):
    """Execute global optimization (does not persist to DB by design)."""
    try:
        # Step 1: Perform curve fitting
        fitting_service = FittingService(req.q_gl_list, req.q_fluid_list, req.wct_list)
        fit = fitting_service.perform_fitting_group()

        # Step 2: Initialize and run global optimization pipeline
        pipeline = OptimizationGlobalPipelineService(
            q_gl_common_range=fit["q_gl_common_range"],
            q_oil_rates_list=fit["q_oil_rates_list"],
            qgl_min=req.qgl_min,
            p_qoil=req.p_qoil,
            p_qgl=req.p_qgl,
            max_iterations=req.max_iterations,
            max_qgl=req.max_qgl
        )
        optimization_results = pipeline.run()

        return clean_numpy_and_nans(optimization_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Global optimization failed: {str(e)}")


@router.get("/history")
def get_optimization_history(
    limit: int = 10, 
    session: Session = Depends(get_db_session)
):
    """Fetch historical field optimization runs."""
    try:
        repo = FieldOptimizationRepository(session)
        service = FieldOptimizationService(repo)
        history = service.list_field_optimizations(limit=limit)
        return [clean_numpy_and_nans(opt.to_dict()) for opt in history]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not retrieve history: {str(e)}")


@router.get("/history/{opt_id}")
def get_optimization_detail(
    opt_id: int, 
    session: Session = Depends(get_db_session)
):
    """Retrieve details of a specific field optimization."""
    try:
        repo = FieldOptimizationRepository(session)
        # Using simple query to find the specific field optimization
        opt = session.get(FieldOptimization, opt_id)
        if not opt:
            raise HTTPException(status_code=404, detail=f"Optimization with ID {opt_id} not found")
        return clean_numpy_and_nans(opt.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not retrieve details for ID {opt_id}: {str(e)}")


@router.get("/history/{opt_id}/wells")
def get_well_optimization_details(
    opt_id: int, 
    session: Session = Depends(get_db_session)
):
    """Fetch the individual well optimization records for a specific field optimization ID."""
    try:
        repo = WellOptimizationRepository(session)
        service = WellOptimizationService(repo)
        well_results = service.get_well_optimizations_by_optimization(opt_id)
        return [clean_numpy_and_nans(w.to_dict()) for w in well_results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not retrieve well results: {str(e)}")
