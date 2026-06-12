import tkinter as tk
from tkinter import ttk
from datetime import datetime


def criar_complemento_garantias(root, frame_garantias, font_style):
    vars_garantias = {}

    opcoes_garantias = [
        ("Aval", "aval"),
        ("Penhor cedular", "penhor_cedular"),
        ("Hipoteca cedular", "hipoteca_cedular"),
    ]

    avales = []
    nome_aval = tk.StringVar(master=root, value="")
    doc_aval = tk.StringVar(master=root, value="")

    frame_aval = ttk.LabelFrame(frame_garantias, text="Avalista(s)")
    frame_penhor = ttk.LabelFrame(frame_garantias, text="Descrição do Penhor Cedular")
    frame_hipoteca = ttk.LabelFrame(frame_garantias, text="Descrição da Hipoteca Cedular")

    ttk.Label(frame_aval, text="Nome:", font=font_style).grid(row=0, column=0, sticky="w", padx=4, pady=2)
    ttk.Entry(frame_aval, textvariable=nome_aval, font=font_style, width=35).grid(row=0, column=1, sticky="w", padx=4, pady=2)

    ttk.Label(frame_aval, text="CPF/CNPJ:", font=font_style).grid(row=1, column=0, sticky="w", padx=4, pady=2)
    ttk.Entry(frame_aval, textvariable=doc_aval, font=font_style, width=25).grid(row=1, column=1, sticky="w", padx=4, pady=2)

    lista_avales = tk.Listbox(frame_aval, height=4, width=60)
    lista_avales.grid(row=3, column=0, columnspan=2, sticky="ew", padx=4, pady=4)

    def adicionar_aval():
        nome = nome_aval.get().strip()
        documento = doc_aval.get().strip()

        if not nome and not documento:
            return

        avales.append({
            "nome": nome,
            "documento": documento
        })

        lista_avales.insert(tk.END, f"{nome} - {documento}")

        nome_aval.set("")
        doc_aval.set("")

    def remover_aval():
        selecionado = lista_avales.curselection()

        if not selecionado:
            return

        index = selecionado[0]
        lista_avales.delete(index)
        avales.pop(index)

    ttk.Button(frame_aval, text="Adicionar avalista", command=adicionar_aval).grid(
        row=2, column=0, sticky="w", padx=4, pady=4
    )

    ttk.Button(frame_aval, text="Remover selecionado", command=remover_aval).grid(
        row=2, column=1, sticky="w", padx=4, pady=4
    )

    txt_penhor = tk.Text(frame_penhor, width=60, height=4, font=font_style)
    txt_penhor.grid(row=0, column=0, padx=4, pady=4)

    txt_hipoteca = tk.Text(frame_hipoteca, width=60, height=4, font=font_style)
    txt_hipoteca.grid(row=0, column=0, padx=4, pady=4)

    def atualizar_campos_garantia():
        if vars_garantias["aval"].get():
            frame_aval.grid(row=3, column=0, columnspan=2, sticky="ew", padx=4, pady=6)
        else:
            frame_aval.grid_remove()

        if vars_garantias["penhor_cedular"].get():
            frame_penhor.grid(row=4, column=0, columnspan=2, sticky="ew", padx=4, pady=6)
        else:
            frame_penhor.grid_remove()

        if vars_garantias["hipoteca_cedular"].get():
            frame_hipoteca.grid(row=5, column=0, columnspan=2, sticky="ew", padx=4, pady=6)
        else:
            frame_hipoteca.grid_remove()

    for i, (rotulo, codigo) in enumerate(opcoes_garantias):
        var_gar = tk.BooleanVar(master=root, value=False)

        tk.Checkbutton(
            frame_garantias,
            text=rotulo,
            variable=var_gar,
            command=atualizar_campos_garantia,
            font=font_style,
            anchor="w",
            justify="left"
        ).grid(row=i, column=0, sticky="w")

        vars_garantias[codigo] = var_gar

    frame_aval.grid_remove()
    frame_penhor.grid_remove()
    frame_hipoteca.grid_remove()

    def obter_resultado_garantias():
        return {
            "opcoes_garantias": [
                codigo for codigo, var in vars_garantias.items()
                if var.get()
            ],
            "complemento_garantias": {
                "aval": avales,
                "penhor_cedular": txt_penhor.get("1.0", "end").strip(),
                "hipoteca_cedular": txt_hipoteca.get("1.0", "end").strip()
            }
        }

    return obter_resultado_garantias

# Função para normalizar datas dos contratos
def normalizar_data(valor):
    valor = valor.strip()

    if not valor:
        return ""

    try:
        data = datetime.strptime(valor, "%d/%m/%Y")
        return data.strftime("%d/%m/%Y")
    except ValueError:
        raise ValueError(f"Data inválida: {valor}. Use o formato dd/mm/aaaa.")