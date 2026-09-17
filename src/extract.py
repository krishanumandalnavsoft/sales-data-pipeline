import pandas as pd

def extract_data(file_path=None):
    df = pd.read_csv(file_path)
    return df