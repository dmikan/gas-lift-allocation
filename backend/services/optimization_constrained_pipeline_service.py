 # services/optimization_pipeline.py
from backend.services.optimization_model_service import OptimizationModel
from backend.services.saving_orchestration_service import SavingOrchestrationService
import numpy as np
from typing import Dict, List, Tuple
from backend.entities.database import SnowflakeDB

class OptimizationConstrainedPipelineService:
    """Handles the optimization process using pre-calculated fitting results"""

    def __init__(self,
                 q_gl_common_range: np.ndarray,
                 q_oil_rates_list: List[np.ndarray],
                 plot_data: List[Dict],
                 list_info: List[str],
                 qgl_limit: float = 4600,
                 qgl_min: float = 0.0,
                 p_qoil: float = 0.0,
                 p_qgl: float = 0.0,
                 db: SnowflakeDB = None):
        """
        Initialize with pre-calculated fitting results

        Args:
            csv_file_path: Path to source CSV file
            q_gl_range: Generated gas lift range
            q_oil_list: Predicted oil rates for each well
            plot_data: Visualization-ready data
            list_info: Well information list
            qgl_limit: Gas lift availability constraint
            p_qoil: Oil price
            p_qgl: Gas lift cost
        """
        #self.csv_file_path = csv_file_path
        self.q_gl_common_range = q_gl_common_range
        self.q_oil_rates_list = q_oil_rates_list
        self.plot_data = plot_data
        self.list_info = list_info
        self.qgl_limit = qgl_limit
        self.qgl_min = qgl_min
        self.p_qoil = p_qoil
        self.p_qgl = p_qgl
        self.model = None
        self.results = None
        self.db = db

    def _calculate_marginal_analysis(self) -> Tuple[List[float], List[float]]:
        """Calculate optimal gas lift rates using marginal analysis"""
        delta_q_gl = np.diff(self.q_gl_common_range)
        p_qgl_optim_list = []
        p_qoil_optim_list = []

        for well in range(len(self.q_oil_rates_list)):
            delta_q_oil = np.diff(self.q_oil_rates_list[well])
            mrp = self.p_qoil * (delta_q_oil / delta_q_gl)
            qgl_values = self.q_gl_common_range[:-1]

            optimal_idx = np.where(mrp >= self.p_qgl)[0][-1] if any(mrp >= self.p_qgl) else len(mrp)-1
            p_qgl_optim_list.append(qgl_values[optimal_idx])
            p_qoil_optim_list.append(self.q_oil_rates_list[well][optimal_idx])

        return p_qgl_optim_list, p_qoil_optim_list

    def _setup_optimization_model(self, p_qgl_optim_list: List[float]):
        """Configure and solve the optimization model"""
        self.model = OptimizationModel(
            q_gl=self.q_gl_common_range,
            q_fluid_wells=self.q_oil_rates_list,
            available_qgl_total=self.qgl_limit,
            qgl_min=self.qgl_min,
            p_qgl_list=p_qgl_optim_list
        )

        self.model.define_optimisation_problem()
        self.model.define_variables()
        self.model.build_objective_function()
        self.model.add_constraints()
        self.model.solve_prob()

    def run(self) -> Dict:
        """
        Execute the optimization pipeline

        Returns:
            Dictionary with all results and visualization data
        """
        # Step 1: Marginal analysis
        p_qgl_optim_list, p_qoil_optim_list = self._calculate_marginal_analysis()

        # Step 2: Setup and solve optimization
        self._setup_optimization_model(p_qgl_optim_list)

        # Step 3: Get results
        result_prod_rates = self.model.get_maximised_prod_rates()
        result_optimal_qgl = self.model.get_optimal_injection_rates()
        self.results = list(zip(result_prod_rates, result_optimal_qgl))

        # Step 4: Save to database
        wells_data = [{
            'well_number': i+1,
            'optimal_production': prod,
            'optimal_gas_injection': qgl,
            'well_name': self.list_info[i+1]
        } for i, (prod, qgl) in enumerate(self.results)]

        data = {
            "total_prod": sum(result_prod_rates),
            "total_qgl": sum(result_optimal_qgl),
            "info": self.list_info,
            "wells_data": wells_data,
            "qgl_limit": self.qgl_limit,
            "oil_price": self.p_qoil,
            "gas_price": self.p_qgl
        }
        result_service = SavingOrchestrationService(self.db)
        result_service.save_constrained_optimization_results(data)


        return {
            "results": self.results,
            "plot_data": self.plot_data,
            "summary": {
                "total_production": sum(result_prod_rates),
                "total_qgl": sum(result_optimal_qgl),
                "qgl_limit": self.qgl_limit
            },
            "q_gl_common_range": self.q_gl_common_range,
            "q_oil_rates_list": self.q_oil_rates_list,
            "p_qgl_optim_list": p_qgl_optim_list,
            "p_qoil_optim_list": p_qoil_optim_list
        }

    def get_well_count(self) -> int:
        """Get the number of wells in the dataset"""
        return len(self.q_oil_list)

    def update_economic_parameters(self,
                                qgl_limit: float = None,
                                p_qoil: float = None,
                                p_qgl: float = None):
        """Update optimization parameters"""
        if qgl_limit is not None:
            self.qgl_limit = qgl_limit
        if p_qoil is not None:
            self.p_qoil = p_qoil
        if p_qgl is not None:
            self.p_qgl = p_qgl