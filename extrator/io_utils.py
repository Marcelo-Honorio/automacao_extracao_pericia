import json
from pathlib import Path
import pandas as pd

# calculo do valor acumulado
def dias_acum(df):
    '''utilizar depois da função classificar e dias'''
    valor = 0
    resultado = []
    for i in df.index:
        if df['historico'][i]=="juros_encarg_add": 
            valor = df['dias'][i]
            resultado.append(valor)
        else:
            valor = df['dias'][i] + valor
            resultado.append(valor)
    return resultado


# df: pd.DataFrame
def salvar_resultados(out_dir: Path, erros: list, alertas: pd.DataFrame, resumo: dict):
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "logs").mkdir(parents=True, exist_ok=True)

    # Excel consolidado
    # df.to_excel(out_dir / "consolidado.xlsx", index=False)

    # Erros (CSVs)
    erros_df = pd.DataFrame(erros)
    erros_df.to_csv(out_dir / "logs" / "erros.csv", index=False, sep=";", encoding="utf-8-sig")

    # Alertas
    alertas.to_csv(out_dir / "logs" / "alertas.csv", index=False, sep=";", encoding="utf-8-sig")

    # Resumo
    with open(out_dir / "logs" / "resumo.json", "w", encoding="utf-8") as f:
        json.dump(resumo, f, ensure_ascii=False, indent=2)