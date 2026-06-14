import pandas as pd
import numpy as np
from typing import List, Tuple, Union

class DataLoader:
    """
    Class to load and preprocess production data (QGL and Qprod)
    from CSV files, supporting different formats.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path

    '''
    Method to load data from UI.
    Returns (QGL_lists, Qprod_lists, Metadata_list).
    '''
    def load_data(self) -> Tuple[List[List[float]], List[List[float]], List[float], List[str]]:
        try:
            df_info = pd.read_csv(self.file_path, nrows=3, header=None)
            df_wct = pd.read_csv(self.file_path, skiprows=3, nrows=1, header=None)
            df_data = pd.read_csv(self.file_path, skiprows=5, header=None)
        except Exception as e:
            print(f"Error reading UI data from {self.file_path}: {e}")
            return [], [], [], []

        field_name = df_info.iloc[2, 0]
        well_names = df_info.iloc[2, 1:].dropna().tolist()
        wct_values = df_wct.iloc[:, 1:].to_numpy().flatten().tolist()
        
        column_labels_qgl = df_data.columns[1::2]
        column_label_prod = df_data.columns[2::2]
        
        # Convert all data columns to numeric, forcing empty spaces to NaN
        df_numeric = df_data.apply(pd.to_numeric, errors='coerce')
        
        list_of_wells_qgl = df_numeric.loc[:, column_labels_qgl].T.to_numpy().tolist()
        list_of_well_prods = df_numeric.loc[:, column_label_prod].T.to_numpy().tolist()
        
        list_of_wells_qgl = [[x for x in q_gl if not np.isnan(x)] for q_gl in list_of_wells_qgl]
        list_of_well_prods = [[x for x in q_oil if not np.isnan(x)] for q_oil in list_of_well_prods]
        
        # Make sure wct values are clean numbers too
        wct_values = [float(x) for x in wct_values if pd.notnull(x) and not np.isnan(x)]
        
        return (list_of_wells_qgl, list_of_well_prods, wct_values, [field_name] + well_names)

    def get_well_names(self) -> List[str]:
        """Extract well names from the loaded data."""
        df_info = pd.read_csv(self.file_path, nrows=3, header=None)
        well_names = df_info.iloc[2, 1:].dropna().tolist()
        
        return well_names