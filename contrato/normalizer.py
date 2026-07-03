from __future__ import annotations

import re
import pandas as pd


def valor_br_para_float(valor):
    if valor is None:
        return None

    if isinstance(valor, (int, float)):
        return float(valor)

    s = str(valor).strip()

    if not s:
        return None

    s = s.replace("R$", "").replace(" ", "")
    s = s.replace(".", "").replace(",", ".")

    try:
        return float(s)
    except ValueError:
        return None


def taxa_br_para_float(valor):
    if valor is None:
        return None

    s = str(valor).strip().replace("%", "").replace(",", ".")

    try:
        return float(s)
    except ValueError:
        return None


def normalizar_data(data):
    if not data:
        return ""

    try:
        dt = pd.to_datetime(data, dayfirst=True, errors="raise")
        return dt.strftime("%d/%m/%Y")
    except Exception:
        return str(data).strip()


def normalizar_regime_capitalizacao(valor):
    if not valor:
        return None

    valor = str(valor).lower().strip()

    if "compost" in valor:
        return "composto"

    if "simples" in valor:
        return "simples"

    if "não informado" in valor or "nao informado" in valor:
        return "nao_informado"

    return None