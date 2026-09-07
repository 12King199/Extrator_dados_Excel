import pandas as pd

def load_excel(path):

    return pd.read_excel(path)

def save_excel(df, path):

    df.to_excel(path, index=False)

def get_missing_columns(row):

    missing = []

    for coluna in row.index:

        if pd.isna(row[coluna]) or str(row[coluna]).strip() == "":

            missing.append(coluna)

    return missing