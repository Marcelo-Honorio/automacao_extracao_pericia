import json
from pathlib import Path
from tkinter import ttk
import tkinter as tk

from contrato.finder import localizar_contrato_pdf
from contrato.extractor import extrair_parametros_contrato


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

## Criar uma pequena janela com um Entry e um botão "Pesquisar"
def localizar_pasta(root, pasta_base: Path, titulo="Localizar pasta"):
    janela = tk.Toplevel(root)
    janela.title(titulo)
    janela.resizable(False, False)

    resultado = {"path": None}

    ttk.Label(
        janela,
        text="Número ou parte do nome da pasta:"
    ).grid(row=0, column=0, padx=10, pady=(10, 2), sticky="w")

    busca = tk.StringVar()

    ttk.Entry(
        janela,
        textvariable=busca,
        width=30
    ).grid(row=1, column=0, padx=10)

    lista = tk.Listbox(janela, width=70, height=12)
    lista.grid(row=2, column=0, padx=10, pady=10)

    def pesquisar():

        lista.delete(0, tk.END)

        termo = busca.get().lower().strip()

        if not termo:
            return

        encontrados = []

        for pasta in pasta_base.rglob("*"):
            if pasta.is_dir() and termo in pasta.name.lower():
                encontrados.append(pasta)

        for pasta in encontrados:
            lista.insert(tk.END, str(pasta))

    def selecionar():
        if not lista.curselection():
            return

        resultado["path"] = Path(lista.get(lista.curselection()[0]))
        janela.destroy()

    ttk.Button(janela, text="Pesquisar", command=pesquisar).grid(
        row=1, column=1, padx=5
    )

    ttk.Button(janela, text="Selecionar", command=selecionar).grid(
        row=3, column=0, pady=(0, 10)
    )

    janela.grab_set()
    root.wait_window(janela)

    return resultado["path"]

## Informações extraidas de contrato
def valor_preenchido(valor):
    return valor not in (None, "", [], {})

def mesclar_parametros(defaults=None, contrato=None, salvos=None):
    """
    Prioridade:
    1. defaults
    2. contrato
    3. salvos

    Ou seja, salvos sobrescrevem contrato,
    e contrato sobrescreve defaults.
    """

    resultado = {}

    for origem in (defaults, contrato, salvos):
        if not origem:
            continue

        for chave, valor in origem.items():
            if valor_preenchido(valor):
                resultado[chave] = valor

    return resultado

# Carregar os parametros do contrato ou já salvos
def obter_parametros_iniciais(parametros_path=None, pasta=None):
    parametros_salvos = {}
    parametros_contrato = {}

    if parametros_path and parametros_path.exists():
        parametros_salvos = carregar_parametros(parametros_path)

        return mesclar_parametros(
            salvos=parametros_salvos,
        )

    try:
        if pasta:
            contrato_pdf = localizar_contrato_pdf(pasta)

            if contrato_pdf:
                parametros_contrato = extrair_parametros_contrato(contrato_pdf)
                print(f"[CONTRATO] Dados extraídos de: {contrato_pdf.name}")
            else:
                print("[CONTRATO] Nenhum contrato PDF localizado.")

    except Exception as e:
        print(f"[CONTRATO] Erro ao extrair dados do contrato: {e}")

    return mesclar_parametros(
        contrato=parametros_contrato,
        salvos=parametros_salvos,
    )
