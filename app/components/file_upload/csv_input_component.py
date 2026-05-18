import streamlit as st
import pandas as pd
from io import StringIO
from app.styles.custom_styles import inject_global_css
from app.utils.state_keys import StateKeys
from pathlib import Path


class CSVInputComponent:
    def __init__(self, tmp_dir: Path):
        self.tmp_dir = tmp_dir
        self.up_file = None

    def load(self):
        inject_global_css()
        self._show_csv_loader_widget()
        self._persistence()

    def _show_csv_loader_widget(self):
        with st.expander("Data Uploader", expanded=True):
            self.up_file = st.file_uploader("Upload csv file with production data", type="csv")


    def _persistence(self):
        if self.up_file is not None:
            content = self.up_file.getvalue()
            decoded_content = content.decode("utf-8")
            df = pd.read_csv(StringIO(decoded_content), header=None)
            tmp_path = self.tmp_dir / "data_csv_file.csv"
            with open(tmp_path, "wb") as f:
                f.write(content)
            self._show_success_banner(tmp_path)


    def _show_success_banner(self, tmp_path):
        st.markdown(f"""
        <div class="save-banner-ok">
          <span style="font-size:18px;">✅</span>
          <div>
            <strong>File loaded successfully</strong>
            <div class="banner-path">{tmp_path}</div>
          </div>
        </div>""", unsafe_allow_html=True)
        st.session_state[StateKeys.SESSION_KEY_DATA_LOAD_MODE] = "csv_upload"
        st.session_state[StateKeys.SESSION_KEY_TEMP_PATH] = tmp_path