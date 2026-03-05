import pandas as pd


def validar_df_basico(df: pd.DataFrame):
    alertas = []

    if df is None or df.empty:
        alertas.append({
            "tipo": "DF_VAZIO",
            "severidade": "BLOQUEIA",
            "mensagem": "DataFrame vazio."
        })
        return alertas

    if len(df) < 3:
        alertas.append({
            "tipo": "POUCAS_LINHAS",
            "severidade": "BLOQUEIA",
            "mensagem": f"Poucas linhas ({len(df)})."
        })

    if "Tipo" in df.columns:
        indef = int((df["Tipo"] == "INDEFINIDO").sum())
        if indef > 0:
            alertas.append({
                "tipo": "TIPO_INDEFINIDO",
                "severidade": "ALERTA",
                "quantidade": indef,
                "mensagem": f"{indef} linhas com Tipo=INDEFINIDO."
            })

    return alertas


def validar_datas_ordenadas(df: pd.DataFrame):
    alertas = []
    if "Data" not in df.columns:
        return alertas

    df_tmp = df.copy()
    df_tmp["Data_dt"] = pd.to_datetime(df_tmp["Data"], dayfirst=True, errors="coerce")

    if df_tmp["Data_dt"].isna().all():
        alertas.append({
            "tipo": "DATA_INVALIDA",
            "severidade": "BLOQUEIA",
            "mensagem": "Nenhuma data pôde ser convertida."
        })
        return alertas

    if not df_tmp["Data_dt"].is_monotonic_increasing:
        alertas.append({
            "tipo": "DATA_FORA_DE_ORDEM",
            "severidade": "ALERTA",
            "mensagem": "Existem datas fora de ordem cronológica."
        })

    return alertas


def validar_saldo_vs_calculado(df: pd.DataFrame, tolerancia=0.01, limite_pct_div=0.10):
    """
    Compara Saldo (PDF) com Saldo_calculado.
    - ALERTA se divergência em poucas linhas
    - BLOQUEIA se divergência em muitas linhas (>= limite_pct_div)
    """
    alertas = []
    if "Saldo" not in df.columns or "Saldo_calculado" not in df.columns:
        return alertas

    df_tmp = df.copy()

    # garante numérico
    df_tmp["Saldo"] = pd.to_numeric(df_tmp["Saldo"], errors="coerce")
    df_tmp["Saldo_calculado"] = pd.to_numeric(df_tmp["Saldo_calculado"], errors="coerce")

    comp = df_tmp.dropna(subset=["Saldo", "Saldo_calculado"])
    if comp.empty:
        return alertas

    diverg = comp[(comp["Saldo"] - comp["Saldo_calculado"]).abs() > tolerancia]
    qtd = int(len(diverg))
    pct = qtd / max(len(comp), 1)

    if qtd == 0:
        return alertas

    sever = "BLOQUEIA" if pct >= limite_pct_div else "ALERTA"
    alertas.append({
        "tipo": "DIVERGENCIA_SALDO",
        "severidade": sever,
        "quantidade": qtd,
        "percentual": round(pct, 4),
        "mensagem": f"Divergência de saldo em {qtd} linhas ({pct:.1%})."
    })

    return alertas

def rodar_validacoes_e_decidir(df: pd.DataFrame):
    """
    Retorna:
      df_alertas: DataFrame com alertas
      decisao: dict com status e pode_calcular
    Regras:
      - se houver qualquer alerta severidade=BLOQUEIA -> BLOQUEADO (não calcula)
      - senão, se houver ALERTA -> ALERTA (pode calcular, mas com aviso)
      - senão -> OK (pode calcular)
    """
    alertas = []
    alertas.extend(validar_df_basico(df))
    alertas.extend(validar_datas_ordenadas(df))
    alertas.extend(validar_saldo_vs_calculado(df))

    df_alertas = pd.DataFrame(alertas)

    if df_alertas.empty:
        return df_alertas, {"status": "OK", "pode_calcular": True, "motivo": ""}

    # normaliza
    sev = set(df_alertas.get("severidade", pd.Series(dtype=str)).fillna("").astype(str).str.upper())

    if "BLOQUEIA" in sev:
        motivos = df_alertas[df_alertas["severidade"].str.upper() == "BLOQUEIA"]["tipo"].tolist()
        return df_alertas, {
            "status": "BLOQUEADO",
            "pode_calcular": False,
            "motivo": " | ".join(motivos)
        }

    # se não bloqueou mas tem alertas
    return df_alertas, {
        "status": "ALERTA",
        "pode_calcular": True,
        "motivo": " | ".join(df_alertas["tipo"].astype(str).tolist())
    }