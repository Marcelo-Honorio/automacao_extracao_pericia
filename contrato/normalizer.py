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

    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        partes = s.split(".")
        if len(partes) > 2:
            s = "".join(partes[:-1]) + "." + partes[-1]

    try:
        return float(s)
    except ValueError:
        return None


def taxa_br_para_float(valor):
    if valor is None:
        return None

    s = str(valor).strip()
    s = s.replace("%", "")
    s = s.replace(",", ".")

    try:
        return float(s)
    except ValueError:
        return None


def normalizar_data(data):
    if not data:
        return ""

    data = str(data).strip().lower()

    meses = {
        "janeiro": "01",
        "fevereiro": "02",
        "março": "03",
        "marco": "03",
        "abril": "04",
        "maio": "05",
        "junho": "06",
        "julho": "07",
        "agosto": "08",
        "setembro": "09",
        "outubro": "10",
        "novembro": "11",
        "dezembro": "12",
    }

    m = re.search(r"(\d{1,2})\s+de\s+([a-zç]+)\s+de\s+(\d{4})", data)

    if m:
        dia = int(m.group(1))
        mes = meses.get(m.group(2))
        ano = m.group(3)

        if mes:
            return f"{dia:02d}/{mes}/{ano}"

    try:
        dt = pd.to_datetime(data, dayfirst=True, errors="raise")
        return dt.strftime("%d/%m/%Y")
    except Exception:
        return str(data).strip()