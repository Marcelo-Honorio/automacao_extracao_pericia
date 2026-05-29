
def fmt_moeda(valor):
    if valor is None:
        return None
    s = f"{valor:,.2f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

# transformar parcelas em string
def fmt_numero(valor):
    return f"{int(valor):02d}"

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
