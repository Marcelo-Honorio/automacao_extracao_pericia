import json

def salvar_resultados(df, parametros, out_dir, stem):
    with open(out_dir/'parametros.txt', 'w') as f:
        json.dump(parametros, f, indent=4)

    df.to_excel(out_dir/f"{stem}(PROCESSADO).xlsx", index=False)