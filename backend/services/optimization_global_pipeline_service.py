from backend.services.optimization_model_service import OptimizationModel
import numpy as np

class OptimizationGlobalPipelineService:
    """Handles the complete optimization workflow from data processing to solution"""

    def __init__(self,
                q_gl_common_range: np.ndarray,
                q_oil_rates_list: list[list],
                qgl_min: int = 0,
                p_qoil: float = 0.0,
                p_qgl: float = 0.0,
                max_iterations: int = 40,
                max_qgl: int = 50000):
        """
        Initialize the optimization pipeline with required parameters

        Args:
            q_gl_common_range: Array of gas lift injection rates
            q_oil_rates_list: List of oil production predictions, following curve fitting
            qgl_min: Minimum gas rate allowed to inject to a well
            p_qoil: Oil price for economic calculation
            p_qgl: Gas lift cost for economic calculation
            max_iterations: number of optimisations to run in global curve
            max_qgl: upper bound of max q_gl it can take
        """
        self.q_gl_common_range = q_gl_common_range
        self.q_oil_rates_list = q_oil_rates_list
        self.qgl_min = qgl_min
        self.p_qoil = p_qoil
        self.p_qgl = p_qgl
        self.model = None
        self.result_prod_rates = None
        self.result_optimal_qgl = None
        self.current_qgl = None
        self.optimization_results = {"qgl_limit": [], "total_production": [], "total_qgl": [], 'summary': {}}
        self.qgl_history = []
        self.qgl_min = 0
        self.max_iterations = max_iterations
        self.max_qgl = max_qgl


    '''
    this method runs the optimization pipeline for a range of gas lift injection rates
    it uses a logspace to generate the range of gas lift injection rates and
    it runs the optimization pipeline for each gas lift injection rate
    it returns the optimization results
    '''
    def run(self) -> dict:
        log_vals = np.logspace(start=1, stop=np.log10(self.max_qgl), num=self.max_iterations)
        log_vals = np.unique(log_vals)
        for i, qgl_limit in enumerate(log_vals):
            dic_optim_result = self._execute(qgl_limit)
            prod_history: list = self._convert_dict_to_list(dic_optim_result, qgl_limit)
            if self._has_stabilized(values=prod_history):
                break
        self._get_global_optimal_values()
        return self.optimization_results

    def _get_global_optimal_values(self):
        last_total_production = self.optimization_results['total_production'][-1]
        last_total_qgl = self.optimization_results['total_qgl'][-1]
        last_qgl = self.optimization_results['qgl_limit'][-1]
        self.optimization_results['summary']['total_production']= last_total_production
        self.optimization_results['summary']['total_qgl']= last_total_qgl
        self.optimization_results['summary']['qgl_limit']= last_qgl
        return


    def _has_stabilized(self, values, window_size=3, tolerance=1e-6) -> bool:
        '''
        This method checks if the gas lift injection rate has stabilized
        it uses a window size to check if the gas lift injection rate has stabilized
        it returns True if the gas lift injection rate has stabilized
        '''
        if len(values) < window_size:
            return False
        recent = values[-window_size:]
        return all(abs(x - recent[0]) < tolerance for x in recent)

    '''
    this method calculates the optimal gas lift rates using marginal analysis
    it returns the optimal gas lift rates for each well
    '''
    def _calculate_marginal_analysis(self) -> list:
        delta_q_gl = np.diff(self.q_gl_common_range)
        p_qgl_optim_list = []

        for well in range(len(self.q_oil_rates_list)):
            delta_q_oil = np.diff(self.q_oil_rates_list[well])
            mp = delta_q_oil / delta_q_gl  # Marginal Product
            mrp = self.p_qoil * mp  # Marginal Revenue Product
            qgl_values = self.q_gl_common_range[:-1]

            # Find last point where MRP >= gas lift cost
            optimal_idx = np.where(mrp >= self.p_qgl)[0][-1] if any(mrp >= self.p_qgl) else len(mrp)-1
            p_qgl_optim_list.append(qgl_values[optimal_idx])
        return p_qgl_optim_list

    '''
    this method sets up the optimization model and configure the optimization model
    with parameters
    '''
    def _setup_optimization_model(self, p_qgl_optim_list: list, qgl_limit: int) -> None:
        self.model = OptimizationModel(
            q_gl=self.q_gl_common_range,
            q_fluid_wells=self.q_oil_rates_list,
            available_qgl_total=qgl_limit,
            qgl_min=self.qgl_min,
            p_qgl_list=p_qgl_optim_list
        )
        self.model.define_optimisation_problem()
        self.model.define_variables()
        self.model.build_objective_function()
        self.model.add_constraints()


    '''
    this method runs the complete optimization pipeline using the other methods
    it returns the optimization results
    '''
    def _execute(self, qgl_limit) -> dict:
        p_qgl_optim_list = self._calculate_marginal_analysis() # Step 1: Marginal analysis
        self._setup_optimization_model(p_qgl_optim_list, qgl_limit) # Step 2: Model setup
        self.model.solve_prob() # Step 3: Solve optimization
        self.result_prod_rates: list[float] = self.model.get_maximised_prod_rates() # Step 4: Get results
        self.result_optimal_qgl: list[float] = self.model.get_optimal_injection_rates()
        return {
            "total_production": sum(self.result_prod_rates),
            "total_qgl": sum(self.result_optimal_qgl),
            "qgl_limit": qgl_limit,
            "well_production_rates": self.result_prod_rates,
            "well_gas_injection_rates": self.result_optimal_qgl
                }

    '''
    this method stores the optimization results in a list
    it returns the list of optimization results
    '''
    def _convert_dict_to_list(self, dic_optim_result, qgl_limit) -> list:
        """Run the complete optimization pipeline"""
        self.optimization_results["qgl_limit"].append(qgl_limit)
        self.optimization_results["total_production"].append(dic_optim_result["total_production"])
        self.optimization_results["total_qgl"].append(dic_optim_result["total_qgl"])
        return self.optimization_results["total_production"]