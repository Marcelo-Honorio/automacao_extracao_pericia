import pandas as pd

from .client import baixar_serie_completa, baixar_periodo
from .store import (
    existe_serie,
    carregar_serie_local,
    salvar_serie_local,
    ultima_data_local,
)
from .config import SERIES


def inicializar_serie(codigo: int) -> pd.DataFrame:
    """
    Baixa a série inteira se ela ainda não existir localmente.
    """
    if existe_serie(codigo):
        return carregar_serie_local(codigo)

    df = baixar_serie_completa(codigo)
    salvar_serie_local(codigo, df)
    return df


def atualizar_serie(codigo: int) -> pd.DataFrame:
    """
    Atualiza somente os meses novos da série.
    """
    if not existe_serie(codigo):
        return inicializar_serie(codigo)

    local = carregar_serie_local(codigo)

    if local.empty:
        novo = baixar_serie_completa(codigo)
        salvar_serie_local(codigo, novo)
        return novo

    ultima = ultima_data_local(codigo)
    hoje = pd.Timestamp.today().normalize()

    faltante = baixar_periodo(
        codigo=codigo,
        data_inicial=ultima.strftime("%Y-%m-%d"),
        data_final=hoje.strftime("%Y-%m-%d"),
    )

    atualizado = (
        pd.concat([local, faltante], ignore_index=True)
        .sort_values("data")
        .drop_duplicates(subset=["data"], keep="last")
        .reset_index(drop=True)
    )

    salvar_serie_local(codigo, atualizado)
    return atualizado


def inicializar_todas_series() -> dict[int, pd.DataFrame]:
    resultado = {}
    for codigo in SERIES:
        resultado[codigo] = inicializar_serie(codigo)
    return resultado


def atualizar_todas_series() -> dict[int, pd.DataFrame]:
    resultado = {}
    for codigo in SERIES:
        resultado[codigo] = atualizar_serie(codigo)
    return resultado


def obter_taxa_por_data(codigo: int, data_ref: str):
    """
    Retorna a última taxa disponível até a data informada.
    data_ref em YYYY-MM-DD
    """
    df = carregar_serie_local(codigo)
    if df.empty:
        return None

    data_ref = pd.Timestamp(data_ref)
    df_filtrado = df[df["data"] <= data_ref]

    if df_filtrado.empty:
        return None

    row = df_filtrado.iloc[-1]
    return {
        "data": row["data"].date(),
        "valor": float(row["valor"]),
    }


def status_series() -> dict[int, dict]:
    resumo = {}

    for codigo in SERIES:
        df = carregar_serie_local(codigo)
        if df.empty:
            resumo[codigo] = {
                "arquivo_existe": False,
                "ultima_data": None,
                "quantidade": 0,
            }
        else:
            resumo[codigo] = {
                "arquivo_existe": True,
                "ultima_data": df["data"].max().date(),
                "quantidade": len(df),
            }

    return resumo