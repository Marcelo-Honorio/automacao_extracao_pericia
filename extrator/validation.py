import pandas as pd


def validar_datas_ordenadas(df: pd.DataFrame):
    """
    Verifica se as datas estão em ordem crescente.
    """
    alertas = []

    if "Data" not in df.columns:
        return alertas

    try:
        df_tmp = df.copy()
        df_tmp["Data_dt"] = pd.to_datetime(df_tmp["Data"], format="%d.%m.%Y", errors="coerce")

        if not df_tmp["Data_dt"].is_monotonic_increasing:
            alertas.append({
                "tipo": "DATA_FORA_DE_ORDEM",
                "mensagem": "Existem datas fora de ordem cronológica."
            })

    except Exception:
        alertas.append({
            "tipo": "ERRO_DATA",
            "mensagem": "Erro ao validar datas."
        })

    return alertas


def validar_saldo_vs_calculado(df: pd.DataFrame, tolerancia=0.01):
    """
    Compara Saldo_num (PDF) com Saldo_calc (recalculado).
    """
    alertas = []

    if "Saldo_num" not in df.columns or "Saldo_calc" not in df.columns:
        return alertas

    divergentes = df[
        (df["Saldo_num"].notna()) &
        (df["Saldo_calc"].notna()) &
        ((df["Saldo_num"] - df["Saldo_calc"]).abs() > tolerancia)
    ]

    for idx, row in divergentes.iterrows():
        alertas.append({
            "tipo": "DIVERGENCIA_SALDO",
            "linha": int(idx),
            "data": row.get("Data"),
            "saldo_pdf": row.get("Saldo_num"),
            "saldo_calc": row.get("Saldo_calc")
        })

    return alertas


def rodar_validacoes(df: pd.DataFrame):
    """
    Executa todas as validações e retorna DataFrame de alertas.
    """
    todas = []
    todas.extend(validar_datas_ordenadas(df))
    todas.extend(validar_saldo_vs_calculado(df))

    return pd.DataFrame(todas)

