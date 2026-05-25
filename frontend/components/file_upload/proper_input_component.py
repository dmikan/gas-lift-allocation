import streamlit as st
import pandas as pd
from pathlib import Path

class ProperInputComponent:
    def __init__(self, tmp_dir):
        self.tmp_dir = tmp_dir
    
    def load(self):
        prosper_data = self._handle_prosper_data()
        if prosper_data is not None and prosper_data[1]:
            st.session_state.data_load_mode = "prosper_data"
            st.session_state.temp_path = prosper_data[1]

    def _handle_prosper_input(self):
        available_fields = ["Prosper_data"]
        selected_field = st.selectbox("Seleccione la planta de petróleo", available_fields)
        if selected_field and st.button(f"Traer datos desde simulador"):
            try:
                # Ajusta esta ruta a tu estructura de proyecto real
                project_root = Path(__file__).parent.parent.parent.parent
                source_path = project_root / 'data' / 'data_field101.csv'
                
                if not source_path.exists():
                    st.error(f"No se encuentra el archivo fuente en el repositorio: data/data_field101.csv")
                    return None, None
                    
                # Leemos el archivo fuente
                df = pd.read_csv(source_path, header=None)
                
                field_name = selected_field.lower().replace(" ", "_")
                temp_path = self.tmp_dir / f"data_{field_name}.csv"
                
                # Guardamos el archivo en la ruta temporal
                df.to_csv(temp_path, index=False, header=False)
                
                st.session_state.uploaded_file = df
                st.success("Datos cargados correctamente desde simulador.")
                return df, temp_path
            except Exception as e:
                st.error(f"Error: {e}")
        return None, None