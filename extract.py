import pandas as pd
import os
import glob
import sys
sys.path.append(r"C:\KRESNA\Data Toolbox\Tools")

def ExtractFiles(InputDataPath:str):
    if InputDataPath.endswith('.xlsx'):
        df = pd.read_excel(InputDataPath,skiprows = 2,header=0)
    elif InputDataPath.endswith('.csv'):
        df = pd.read_csv(InputDataPath,skiprows = 2, header=0)
    else:
        raise ValueError("File format not supported. Only .xlsx and .csv are allowed.")    
    
    df.columns = df.columns.str.strip()
    
    return df