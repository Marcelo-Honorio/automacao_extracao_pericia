from pathlib import Path
import pandas as pd

from .config import DATA_DIR, SERIES


def caminho_serie(codigo: int) -> Path:
    if codigo not in SERIES:
        raise ValueError(f"Código de série não cadastrado: {codigo}")
    return DATA_DIR / SERIES[codigo]


def existe_serie(codigo: int) -> bool:
    return caminho_serie(codigo).exists()


def carregar_serie_local(codigo: int) -> pd.DataFrame:
    path = caminho_serie(codigo)

    if not path.exists():
        return pd.DataFrame(columns=["data", "valor"])

    df = pd.read_csv(path)
    if df.empty:
        return pd.DataFrame(columns=["data", "valor"])

    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

    df = (
        df.dropna(subset=["data", "valor"])
        .sort_values("data")
        .reset_index(drop=True)
    )
    return df


def salvar_serie_local(codigo: int, df: pd.DataFrame) -> None:
    path = caminho_serie(codigo)

    df_to_save = df.copy()
    df_to_save["data"] = pd.to_datetime(df_to_save["data"]).dt.strftime("%Y-%m-%d")
    df_to_save.to_csv(path, index=False, sep=";")


def ultima_data_local(codigo: int):
    df = carregar_serie_local(codigo)
    if df.empty:
        return None
    return df["data"].max()