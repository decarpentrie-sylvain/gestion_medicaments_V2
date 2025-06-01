import pandas as pd

def lire_fichier(chemin: str):
    """
    Ouvre un fichier CSV ou Excel et renvoie un DataFrame + son extension.
    """
    ext = chemin.lower().split(".")[-1]
    if ext == "csv":
        df = pd.read_csv(chemin, dtype=str)
        return df, "csv"
    elif ext in ("xls", "xlsx"):
        df = pd.read_excel(chemin, dtype=str)
        return df, "xlsx"
    else:
        raise ValueError(f"Format non pris en charge : {ext}")

def normaliser_colonnes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renomme les colonnes pour uniformiser (minuscule + underscore).
    """
    mapping = {}
    for c in df.columns:
        key = c.strip().lower().replace(" ", "_")
        mapping[c] = key
    df.rename(columns=mapping, inplace=True)
    return df