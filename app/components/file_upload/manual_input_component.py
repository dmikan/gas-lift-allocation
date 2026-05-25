import uuid
import streamlit as st
import pandas as pd
from pathlib import Path
from app.styles.custom_styles import inject_global_css
from app.utils.state_keys import StateKeys
from app.utils.api_client import APIClient




class ManualInputComponent:
    def __init__(self, tmp_dir: Path):
        self.tmp_dir: Path = tmp_dir
        self.num_wells: int = 5
        self.num_rows: int = 1
        self.field_labels: list[str] = []
        self.wct_labels: list[str] = []
        self.prod_labels: list[str] = []

        # Initialize global state to avoid resets
        st.session_state[StateKeys.SESSION_KEY_INFO_DF] = pd.DataFrame()
        st.session_state[StateKeys.SESSION_KEY_WCT_DF] = pd.DataFrame()
        st.session_state[StateKeys.SESSION_KEY_PROD_DF] = pd.DataFrame()
        st.session_state[StateKeys.SESSION_KEY_FINAL_DF] = pd.DataFrame()

    def load(self):
        """Load the manual input component."""
        inject_global_css()
        self._render_data_editor()
        self._show_saved_banner_outside_expander()


    def _render_data_editor(self):
        """Render the data editor."""
        expander = st.expander("Data Editor", expanded=True)
        with expander:
            self._choose_number_of_wells()
            self._generate_labels()
            self._generate_dataframe_editors()
            self._build_and_save_data()

    def _build_and_save_data(self):
        """Build and save the final DataFrame."""
        if st.button("Save all data", key="save_button", type="primary", use_container_width=True):
            self._build_final_dataframe()
            self._persistence()

    def _show_saved_banner_outside_expander(self):
        """Show 'Data saved successfully' below the Data Editor expander."""
        if "_manual_saved_path" in st.session_state and st.session_state["_manual_saved_path"] is not None:
            _saved_success_banner(Path(st.session_state["_manual_saved_path"]))

    def _choose_number_of_wells(self):
        """Choose the number of wells."""
        self.num_wells = st.number_input("Set number of wells", min_value=1, max_value=10, value=5)

    def _generate_labels(self):
        """Generate labels for the data editor."""
        self.info_labels = ["Field"] + [f"Well {i+1}" for i in range(self.num_wells)]
        self.wct_labels = [f"wct {i+1}" for i in range(self.num_wells)]
        self.prod_labels = [item for i in range(1, self.num_wells + 1) for item in (f"qgl {i}", f"ql {i}")]


    @st.fragment
    def _generate_dataframe_editors(self):
        """Keeps keyboard focus and Tab navigation."""
        self._column_config()
        self._sync_dataframe(StateKeys.SESSION_KEY_INFO_DF, self.info_labels, 1)
        self._sync_dataframe(StateKeys.SESSION_KEY_WCT_DF, self.wct_labels, 1)
        self._sync_dataframe(StateKeys.SESSION_KEY_PROD_DF, self.prod_labels, self.num_rows)

        tab1, tab2, tab3 = st.tabs(["Fields & Wells", "Water-Cut Threshold", "Production Data"])
        with tab1:
            _panel_open("📍",
            "Define the field name and assign identifiers for each well.",
            f"{self.num_wells} well configured")
            
            api_client = APIClient()
            wells_list = api_client.get_wells()  # Fetch well list from the API

            
            df_actual = st.session_state[StateKeys.SESSION_KEY_INFO_DF]
            column_configuration = {
                column: st.column_config.SelectboxColumn(
                    f"Well {i+1}", 
                    help="Select a well",
                    width="auto",
                    options=wells_list,
                    required=True,
                )
                for i, column in enumerate(df_actual.columns[1:]) 
            }                      
                        
            st.session_state[StateKeys.SESSION_KEY_INFO_DF] = st.data_editor(
                st.session_state[StateKeys.SESSION_KEY_INFO_DF],
                key="editor_fields",
                column_config=column_configuration,
                hide_index=True,
                use_container_width=True,
            )

        with tab2:
            _panel_open("📉",
            "Set the water-cut threshold (WCT) for each well.",
            f"One row · {self.num_wells} wells")
            st.session_state[StateKeys.SESSION_KEY_WCT_DF] = st.data_editor(
                st.session_state[StateKeys.SESSION_KEY_WCT_DF],
                key="editor_wct",
                hide_index=True,
                use_container_width=True,
            )

        with tab3:
            _panel_open("📊",
            "Enter daily injection rates and fluid types for the simulation.",
            f"{self.num_rows} data rows · {self.num_wells * 2} columns")
            st.session_state[StateKeys.SESSION_KEY_PROD_DF] = st.data_editor(
                st.session_state[StateKeys.SESSION_KEY_PROD_DF],
                column_config=self.column_config,
                key="editor_prod",
                hide_index=True,
                use_container_width=True,
                num_rows="dynamic"
            )

    def _column_config(self):
        """Configure the columns for the production data."""
        self.column_config = {
            col: st.column_config.TextColumn(
                label=col,
                default="", 
            ) 
            for col in self.prod_labels
        }    

    def _sync_dataframe(self, key, labels, rows):
        """Sync data without losing what was written."""
        current = st.session_state.get(key)
        new_df = pd.DataFrame("", index=range(rows), columns=labels)
        if not current.empty:
            common_cols = [c for c in labels if c in current.columns]
            rows_to_copy = min(len(current), rows)
            new_df.iloc[:rows_to_copy][common_cols] = current.iloc[:rows_to_copy][common_cols]
        st.session_state[key] = new_df


    def _build_final_dataframe(self):
        """Build the final DataFrame for optimization."""
        try:
            f_df = st.session_state[StateKeys.SESSION_KEY_INFO_DF]
            w_df = st.session_state[StateKeys.SESSION_KEY_WCT_DF]
            p_df = st.session_state[StateKeys.SESSION_KEY_PROD_DF]

            n_cols = len(p_df.columns) + 1
            final = pd.DataFrame(columns=range(n_cols))
            
            final.loc[0] = ["description"] + [""] * (n_cols - 1)
            final.loc[1] = f_df.columns.tolist() + [""] * (n_cols - len(f_df.columns))
            final.loc[2] = f_df.iloc[0].tolist() + [""] * (n_cols - len(f_df.columns))
            final.loc[3] = ["wct"] + w_df.iloc[0].tolist() + [""] * (n_cols - len(w_df.columns) - 1)
            final.loc[4] = ["index"] + p_df.columns.tolist()

            for i, (idx, row) in enumerate(p_df.iterrows()):
                final.loc[5 + i] = [i + 1] + row.tolist()

            st.session_state[StateKeys.SESSION_KEY_FINAL_DF] = final
        except Exception as e:
            st.error(f"Error building DataFrame: {e}")


    def _persistence(self):
        """Save the final DataFrame to a CSV file."""
        final_df = st.session_state[StateKeys.SESSION_KEY_FINAL_DF]
        if final_df is not None:
            try:
                field_name = final_df.iloc[2, 0] or "manual_data"
                uid = uuid.uuid4().hex[:8]
                filename = f"data_{str(field_name).lower().replace(' ', '_')}_{uid}.csv"
                temp_path: Path = self.tmp_dir / filename
                final_df.to_csv(temp_path, index=False, header=False)

                st.session_state[StateKeys.SESSION_KEY_TEMP_PATH] = temp_path
                st.session_state[StateKeys.SESSION_KEY_DATA_LOAD_MODE] = "manual_input"
                st.session_state["_manual_saved_path"] = temp_path

            except Exception as e:
                st.error(f"Error saving file: {e}")

def _panel_open(icon, caption, badge=None):
    badge_html = f'<span class="panel-badge">⬡ {badge}</span>' if badge else ""
    st.markdown(f"""
    <div class="panel-head">
      <div class="panel-head-row">
        <span class="panel-head-icon">{icon}</span>
        <div class="panel-head-caption">{caption}</div>
      </div>
      {badge_html}
    </div>""", unsafe_allow_html=True)


def _saved_success_banner(temp_path: Path):
    st.markdown(f"""
    <div class="save-banner-ok">
      <span style="font-size:18px;">✅</span>
      <div>
        <strong>Data saved successfully</strong>
        <div class="banner-path">{temp_path}</div>
      </div>
    </div>""", unsafe_allow_html=True)