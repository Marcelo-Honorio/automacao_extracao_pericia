import json
from pathlib import Path


def salvar_parametros(path: Path, parametros: dict):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(parametros, f, ensure_ascii=False, indent=4)

def carregar_parametros(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_resultados(df, parametros, out_dir, stem):
    with open(out_dir/'parametros.txt', 'w') as f:
        json.dump(parametros, f, indent=4)

    df.to_excel(out_dir/"ESPELHO_do_CALCULO.xlsx", index=False)