from datetime import datetime

def fmt_moeda(valor):
    if valor is None:
        return ""
    s = f"{valor:,.2f}"
    return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_percentual(valor):
    if valor is None:
        return ""
    return f"{valor:.4f}%".replace(".", ",")

def fmt_data(valor):
    if valor is None:
        return ""
    if isinstance(valor, str):
        return valor
    return valor.strftime("%d/%m/%Y")
