import streamlit as st
from frontend.utils.state_keys import StateKeys
from frontend.components.optimization.display_constrained_results import DisplayConstrainedResults
from frontend.components.optimization.display_global_results import DisplayGlobalResults
from frontend.components.optimization.reports import OptimizationReportGenerator

class OptimizationResultsComponent:
    """Component responsible exclusively for displaying, toggling, and exporting optimization results."""

    def __init__(self, api_client):
        self.api_client = api_client

    def show(self, loaded_data: any):
        """Render the complete Results of Optimization section."""
        head_col, btn_col = st.columns([4, 1])
        with head_col:
            st.subheader("Results of Optimization")
        with btn_col:
            self._show_export_pdf_button(loaded_data)

        last_tab = st.session_state.get(StateKeys.SESSION_KEY_LAST_OPTIMIZATION_TAB, "constrained")

        # Renders Constrained Results
        with st.expander("Constrained optimization results", expanded=(last_tab != "global")):
            self._render_constrained_results()

        # Renders Global Results
        with st.expander("Global optimization results", expanded=(last_tab == "global")):
            self._render_global_results(loaded_data)

    def _show_export_pdf_button(self, loaded_data: any):
        """Show 'Export to PDF' button when there is at least one active result to generate."""
        has_constrained = (
            StateKeys.SESSION_KEY_CONSTR in st.session_state
            and StateKeys.SESSION_KEY_WELL in st.session_state
        )
        has_global = StateKeys.SESSION_KEY_GLOBAL in st.session_state
        if not (has_constrained or has_global):
            return
            
        list_info = ["Unknown Field"]
        if loaded_data is not None:
            _, _, _, list_info = loaded_data
            
        try:
            # Fetch well tests once so the PDF mirrors the full UI content
            well_results = st.session_state.get(StateKeys.SESSION_KEY_WELL) or []
            well_tests = None
            if well_results:
                well_names = [getattr(r, 'well_name', '') for r in well_results if getattr(r, 'well_name', '')]
                if well_names:
                    try:
                        well_tests = self.api_client.get_latest_well_tests(well_names)
                    except Exception:
                        pass

            gen = OptimizationReportGenerator(
                constrained_optimization_results=st.session_state.get(StateKeys.SESSION_KEY_CONSTR),
                well_results=well_results,
                global_optimization_results=st.session_state.get(StateKeys.SESSION_KEY_GLOBAL),
                list_info=list_info,
                well_tests=well_tests,
                oil_opt_at_baseline=st.session_state.get("oil_opt_at_baseline"),
            )
            pdf_bytes = gen.build_pdf()
            st.download_button(
                "Generate report in PDF",
                data=pdf_bytes,
                file_name="optimization_report.pdf",
                mime="application/pdf",
                key="optimization_export_pdf",
                type="primary",
                use_container_width=True,
            )
        except Exception as e:
            st.caption(f"PDF export unavailable: {e}")

    def _render_constrained_results(self):
        """Renders the summary and metrics for constrained runs."""
        if (StateKeys.SESSION_KEY_CONSTR in st.session_state
                and StateKeys.SESSION_KEY_WELL in st.session_state):
            display = DisplayConstrainedResults(
                st.session_state[StateKeys.SESSION_KEY_CONSTR],
                st.session_state[StateKeys.SESSION_KEY_WELL],
            )
            display.show_detailed_results_by_well()
            c1, c2 = st.columns([1, 2])
            with c1:
                display.show_summary_metrics()
                st.markdown("---")
            with c2:
                display.show_production_curves()
        else:
            self._show_no_optimization_message("constrained")

    def _render_global_results(self, loaded_data: any):
        """Renders the curve and metrics for global runs."""
        if StateKeys.SESSION_KEY_GLOBAL in st.session_state:
            list_info = ["Unknown Field"]
            if loaded_data is not None:
                _, _, _, list_info = loaded_data
            display = DisplayGlobalResults(
                st.session_state[StateKeys.SESSION_KEY_GLOBAL],
                list_info,
                loaded_data,
            )
            g1, g2 = st.columns([1, 5])
            with g1:
                display.show_summary_metrics()
            with g2:
                display.show_global_curve()
        else:
            self._show_no_optimization_message("global")

    def _show_no_optimization_message(self, optimization_type: str):
        """Message when no optimization has been run yet."""
        st.info(
            f"No {optimization_type} optimization has been run yet. Run one by choosing the parameters in the Optimizer."
        )
