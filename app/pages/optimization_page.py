import streamlit as st
from pathlib import Path
from app.components.file_upload.file_upload_component import FileUploadComponent
from app.components.optimization.optimization_settings import OptimizationSettingsComponent
from app.components.optimization.optimization_history import OptimizationHistoryComponent
from app.components.optimization.optimization_execution import OptimizationExecutionComponent
from app.components.optimization.display_constrained_results import DisplayConstrainedResults
from app.components.optimization.display_global_results import DisplayGlobalResults
from app.components.optimization.optimization_report_generator import OptimizationReportGenerator
from backend.entities.database import SnowflakeDB
from backend.services.data_loader_service import DataLoader
from app.utils.state_keys import StateKeys

class OptimizationPage:
    def __init__(self):
        self.db = SnowflakeDB()
        self.file_upload = FileUploadComponent()
        self.loaded_data = None
        self.optimization_settings = OptimizationSettingsComponent()
        self.optimization_execution = OptimizationExecutionComponent(self.db)
        self.optimization_history = OptimizationHistoryComponent(self.db)

    def show(self):
        """
        This method is called by the app to show the optimization page.
        It is called once when the user navigates to the optimization page.
        """
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Data loading")
            self.file_upload.show()

        # Recompute after file_upload.show() so we pick up temp_path set in this run
        temp_path = st.session_state.get(StateKeys.SESSION_KEY_TEMP_PATH)
        is_data_ready = temp_path is not None and Path(temp_path).exists()
        if is_data_ready and self.loaded_data is None:
            self.loaded_data = DataLoader(temp_path).load_data()

        with col2:
            st.subheader("Optimizer")
            self._show_tabs(is_data_ready)

        st.divider()
        self._show_results_of_optimization()

    def _show_results_of_optimization(self):
        """Section 'Results of Optimization'. Order always: 1 Constrained, 2 Global. The one run last is expanded by default."""
        head_col, btn_col = st.columns([4, 1])
        with head_col:
            st.subheader("Results of Optimization")
        with btn_col:
            self._show_export_pdf_button()

        last_tab = st.session_state.get(StateKeys.SESSION_KEY_LAST_OPTIMIZATION_TAB, "constrained")

        with st.expander("Constrained optimization results", expanded=(last_tab != "global")):
            self._render_constrained_results()

        with st.expander("Global optimization results", expanded=(last_tab == "global")):
            self._render_global_results()

    def _show_export_pdf_button(self):
        """Show 'Export to PDF' button when there is at least one result to export."""
        has_constrained = (
            StateKeys.SESSION_KEY_CONSTR in st.session_state
            and StateKeys.SESSION_KEY_WELL in st.session_state
        )
        has_global = StateKeys.SESSION_KEY_GLOBAL in st.session_state
        if not (has_constrained or has_global):
            return
        list_info = ["Unknown Field"]
        if self.loaded_data is not None:
            _, _, _, list_info = self.loaded_data
        try:
            gen = OptimizationReportGenerator(
                constrained_optimization_results=st.session_state.get(StateKeys.SESSION_KEY_CONSTR),
                well_results=st.session_state.get(StateKeys.SESSION_KEY_WELL),
                global_optimization_results=st.session_state.get(StateKeys.SESSION_KEY_GLOBAL),
                list_info=list_info,
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
        if (StateKeys.SESSION_KEY_CONSTR in st.session_state
                and StateKeys.SESSION_KEY_WELL in st.session_state):
            display = DisplayConstrainedResults(
                st.session_state[StateKeys.SESSION_KEY_CONSTR],
                st.session_state[StateKeys.SESSION_KEY_WELL],
            )
            c1, c2 = st.columns([1, 2])
            with c1:
                display.show_summary_metrics()
                st.markdown("---")
                display.show_detailed_results_by_well()
            with c2:
                display.show_production_curves()
        else:
            self._show_no_optimization_message("constrained")

    def _render_global_results(self):
        if StateKeys.SESSION_KEY_GLOBAL in st.session_state:
            list_info = ["Unknown Field"]
            if self.loaded_data is not None:
                _, _, _, list_info = self.loaded_data
            display = DisplayGlobalResults(
                st.session_state[StateKeys.SESSION_KEY_GLOBAL],
                list_info,
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
            "No optimization has been run yet. Run one by choosing the parameters in the Optimizer."
        )

    def _show_tabs(self, is_data_ready):
        """
        This method is called by the app to show the tabs.
        It is called once when the user navigates to the optimization page.
        """
        tab1, tab2, tab3 = st.tabs([
            "Constrained Optimization",
            "Global Optimization",
            "Optimization History"
        ])
        with tab1:
            if is_data_ready:
                with st.expander("Configuration of Optimization", expanded=True):
                    constrained_settings = self.optimization_settings.choose_constrained_settings(
                        use_expander=False,
                        render_button=lambda s: self.optimization_execution.run_constrained_optimization(
                            self.loaded_data, s, message_outside=True
                        ),
                    )
                if StateKeys.SESSION_KEY_CONSTR in st.session_state and StateKeys.SESSION_KEY_WELL in st.session_state:
                    self.optimization_execution.optimization_completed_message(flag="constrained")
            else:
                self._show_warning()

        with tab2:
            if is_data_ready:
                with st.expander("Global Optimization Configuration", expanded=True):
                    global_settings = self.optimization_settings.choose_global_settings(
                        use_expander=False,
                        render_button=lambda s: self.optimization_execution.run_global_optimization(
                            self.loaded_data, s, message_outside=True
                        ),
                    )
                if StateKeys.SESSION_KEY_GLOBAL in st.session_state:
                    self.optimization_execution.optimization_completed_message(flag="global")
            else:
                self._show_warning()

        with tab3:
            with st.container():
                self.optimization_history.show()
                #self.optimization_history.show_optimization_history()
                #self.optimization_history.show_well_details()



    def _show_warning(self):
        """
        Display a warning banner when no data has been loaded for optimization.
        """
        st.markdown("""
            <div class="banner-warning">
              <span>⚠️</span>
              <div>
                <strong>Please load data first to perform the optimization</strong>
                <div class="banner-warning-text"> Use the "Data Editor" or "Upload Data" tab to load data.</div>
              </div>
            </div>""", unsafe_allow_html=True)