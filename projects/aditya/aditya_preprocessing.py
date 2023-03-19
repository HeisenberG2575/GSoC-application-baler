import pandas as pd
import uproot

def pre_processing(input_path,output_path):

    dropped_variables = [
        "Run",
        "Lumi",
        "Event",
        "nJets",
        "nBJets"]
    
    # Load data
    df = pd.read_csv(input_path)
    # Clean data
    df = df.drop(columns=dropped_variables)
    df = df.reset_index(drop=True)
    df = df.dropna()
    global cleared_column_names
    cleared_column_names = list(df)
    df.to_pickle(output_path)
