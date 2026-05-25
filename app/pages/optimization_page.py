import streamlit as st
from pathlib import Path
from app.components.file_upload.file_upload_component import FileUploadComponent
from app.components.optimization.optimization_settings import OptimizationSettingsComponent
from app.components.optimization.optimization_history import OptimizationHistoryComponent
from app.components.optimization.optimization_execution import OptimizationExecutionComponent
from app.components.optimization.optimization_results import OptimizationResultsComponent
from app.utils.api_client import APIClient
from app.utils.state_keys import StateKeys

class OptimizationPage:
    """Page component responsible solely for high-level visual grid layout and tabs coordination."""

    def __init__(self):
        self.api_client = APIClient()
        self.file_upload = FileUploadComponent()
        self.loaded_data = None
        self.optimization_settings = OptimizationSettingsComponent()
        self.optimization_execution = OptimizationExecutionComponent()
        self.optimization_history = OptimizationHistoryComponent()
        self.optimization_results_component = OptimizationResultsComponent(self.api_client)

    def show(self):
        """Render the layout columns and coordination of data loading and results rendering."""
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Data loading")
            self.file_upload.show()

        # Recompute after file_upload.show() so we pick up temp_path set in this run
        temp_path = st.session_state.get(StateKeys.SESSION_KEY_TEMP_PATH)
        is_data_ready = temp_path is not None and Path(temp_path).exists()
        if is_data_ready and self.loaded_data is None:
            import os
            try:
                with open(temp_path, "rb") as f:
                    file_bytes = f.read()
                filename = os.path.basename(temp_path)
                self.loaded_data = self.api_client.load_data(file_bytes, filename)
            except Exception as e:
                st.error(f"Error reading file: {e}")

        with col2:
            st.subheader("Optimizer")
            self._show_tabs(is_data_ready)

        st.divider()
        self.optimization_results_component.show(self.loaded_data)

    def _show_tabs(self, is_data_ready: bool):
        """Show the optimization configurations and history tabs."""
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

    def _show_warning(self):
        """Display a warning banner when no data has been loaded for optimization."""
        st.markdown("""
            <div class="banner-warning">
              <span>⚠️</span>
              <div>
                <strong>Please load data first to perform the optimization</strong>
                <div class="banner-warning-text"> Use the "Data Editor" or "Upload Data" tab to load data.</div>
              </div>
            </div>""", unsafe_allow_html=True)