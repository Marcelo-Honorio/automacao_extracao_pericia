from io import StringIO
from datetime import datetime
import pandas as pd
import requests

from .config import BASE_URL, TIMEOUT


def _ler_csv_bcb(texto: str) -> pd.DataFrame:
    if not texto.strip():
        return pd.DataFrame(columns=["data", "valor"])

    df = pd.read_csv(StringIO(texto), sep=";")
    df.columns = [c.strip().lower() for c in df.columns]

    if "data" not in df.columns or "valor" not in df.columns:
        raise ValueError("Resposta da API não contém colunas 'data' e 'valor'.")

    df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce")

    df["valor"] = (
        df["valor"]
        .astype(str)
        .str.strip()
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

    df = df.dropna(subset=["data", "valor"]).copy()
    df = df.sort_values("data").reset_index(drop=True)
    return df[["data", "valor"]]


def baixar_serie_completa(codigo: int) -> pd.DataFrame:
    url = BASE_URL.format(codigo=codigo)
    resp = requests.get(url, timeout=TIMEOUT)
    resp.raise_for_status()
    return _ler_csv_bcb(resp.text)


def baixar_periodo(codigo: int, data_inicial: str, data_final: str) -> pd.DataFrame:
    """
    data_inicial e data_final em YYYY-MM-DD
    """
    di = datetime.strptime(data_inicial, "%Y-%m-%d").strftime("%d/%m/%Y")
    df = datetime.strptime(data_final, "%Y-%m-%d").strftime("%d/%m/%Y")

    url = (
        BASE_URL.format(codigo=codigo)
        + f"&dataInicial={di}&dataFinal={df}"
    )
    resp = requests.get(url, timeout=TIMEOUT)
    resp.raise_for_status()
    return _ler_csv_bcb(resp.text)