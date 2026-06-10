import tkinter as tk
from tkinter import ttk


def create_input_with_options(steam: str, parent=None):
    resultado = {}

    root = tk.Toplevel()
    root.title("Entrada Manual")
    root.resizable(True, True)
    font_style = ("Arial", 12)

    def salvar():
        nonlocal resultado
        resultado = {
            "autor": tipo_autor.get(),
            "instrumento": tipo_doc.get(),
            "cliente": nome_cliente.get(),
            "agente": tipo_agente.get(),
            "contrato": contrato_n.get(),
            "valor_liberado": valor_liberado.get(),
            "periodo": periodo_var.get(),
            "estornos": [codigo for codigo, var in vars_estorno.items() if var.get()],
            "juros": juros_var.get(),
            "tx_mercado": tx_mercado.get(),
            "valor_parcela": valor_parcela.get(),
            "numero_parcela": numero_parcela.get(),
            "tx_equivalente": tx_equivalente_var.get(),
            "opcoes_inadimplento": [codigo for codigo, var in vars_inadimplemento.items() if var.get()],
            "opcoes_garantias": [codigo for codigo, var in vars_garantias.items() if var.get()],
            "finalidade_op": finalidade_op.get(),
            "Capitalização": {
                "existe_capitalizacao": existe_cap_var.get() == "Sim",
                "periodicidade_capitalizacao": periodicidade_cap_var.get(),
                "taxa_anual_supera_duodecuplo": (
                    True if taxa_supera_var.get() == "Sim"
                    else False if taxa_supera_var.get() == "Não"
                    else None
                ),
                "regime_capitalizacao": regime_cap_var.get()
            }
        }
        root.quit()
        root.destroy()

    def cancelar():
        root.quit()
        root.destroy()

    ttk.Label(root, text=f"Arquivo: {steam}", font=14).grid(row=0, column=0, columnspan=2, pady=5)

    ttk.Label(root, text="Autor:", font=font_style).grid(row=1, column=0, sticky="w")
    tipo_autor = tk.StringVar(master=root, value="Banco do Brasil S.A.")
    ttk.Combobox(
        root,
        values=["Banco do Brasil S.A.", "Banco Santander S.A.", "Caixa Econômica Federal", "Banco Bradesco S.A."],
        textvariable=tipo_autor,
        font=font_style
    ).grid(row=1, column=1, pady=2)

    ttk.Label(root, text="Tipo operação:", font=font_style).grid(row=2, column=0, sticky="w")
    tipo_doc = tk.StringVar(master=root, value="Cédula Rural Pignoratícia")
    opcoes_doc = [
        "Cédula Rural Pignoratícia",
        "Cédula Rural Hipotecária",
        "Cédula Rural Pignoratícia e Hipotecária",
        "Nota de Crédito Rural",
        "Cédula de Produto Rural",
        "Cédula de Crédito Bancário"
    ]
    ttk.Combobox(root, values=opcoes_doc, textvariable=tipo_doc, font=font_style).grid(row=2, column=1, pady=2)

    ttk.Label(root, text="Cliente(s):", font=font_style).grid(row=3, column=0, sticky="w")
    nome_cliente = tk.StringVar(master=root, value="")
    ttk.Entry(root, textvariable=nome_cliente, font=font_style).grid(row=3, column=1, pady=2)

    ttk.Label(root, text="Agente(s):", font=font_style).grid(row=4, column=0, sticky="w")
    tipo_agente = tk.StringVar(master=root, value="do réu")
    ttk.Combobox(
        root,
        values=["do réu", "da ré", "dos réus", "das rés"],
        textvariable=tipo_agente,
        font=font_style
    ).grid(row=4, column=1, pady=2)

    ttk.Label(root, text="Número da operação:", font=font_style).grid(row=5, column=0, sticky="w")
    contrato_n = tk.StringVar(master=root, value="0")
    ttk.Entry(root, textvariable=contrato_n, font=font_style).grid(row=5, column=1, pady=2)

    ttk.Label(root, text="Valor liberado/solicitado:", font=font_style).grid(row=6, column=0, sticky="w")
    valor_liberado = tk.DoubleVar(master=root, value=0)
    ttk.Entry(root, textvariable=valor_liberado, font=font_style).grid(row=6, column=1, pady=2)

    ttk.Label(root, text="Período:", font=font_style).grid(row=7, column=0, sticky="w")
    periodo_var = tk.StringVar(master=root, value="mensal")
    ttk.Combobox(
        root,
        values=["mensal", "cobrança única"],
        textvariable=periodo_var,
        font=font_style
    ).grid(row=7, column=1, pady=2)

    ttk.Label(root, text="Estornos:", font=font_style).grid(row=8, column=0, sticky="w")
    opcoes_estorno = [
        ("Seguro Penhor", "seguro_penhor"),
        ("Seguro de Vida", "seguro_vida"),
        ("Seguro Agrícola", "seguro_agricola"),
        ("Juros de Mora", "juros_mora"),
        ("Tarifa", "tarifa"),
    ]
    frame_estorno = ttk.Frame(root)
    frame_estorno.grid(row=8, column=1, pady=2, padx=6, sticky="w")
    vars_estorno = {}

    for i, (rotulo, codigo) in enumerate(opcoes_estorno):
        var_estorno = tk.BooleanVar(master=root, value=False)
        tk.Checkbutton(
            frame_estorno,
            text=rotulo,
            variable=var_estorno,
            font=font_style,
            anchor="w",
            justify="left"
        ).grid(row=i, column=0, sticky="w")
        vars_estorno[codigo] = var_estorno

    ttk.Label(root, text="Taxa equivalente:", font=font_style).grid(row=9, column=0, sticky="w")
    tx_equivalente_var = tk.StringVar(master=root, value="diaria")
    ttk.Combobox(
        root,
        values=["base30", "diaria"],
        textvariable=tx_equivalente_var,
        font=font_style
    ).grid(row=9, column=1, pady=2)

    ttk.Label(root, text="Taxa de juros efetiva:", font=font_style).grid(row=10, column=0, sticky="w")
    juros_var = tk.DoubleVar(master=root, value=0.00)
    ttk.Entry(root, textvariable=juros_var, font=font_style).grid(row=10, column=1, pady=2)

    ttk.Label(root, text="Valor da parcela:", font=font_style).grid(row=11, column=0, sticky="w")
    valor_parcela = tk.DoubleVar(master=root, value=0)
    ttk.Entry(root, textvariable=valor_parcela, font=font_style).grid(row=11, column=1, pady=2)

    ttk.Label(root, text="Número de parcelas:", font=font_style).grid(row=12, column=0, sticky="w")
    numero_parcela = tk.IntVar(master=root, value=0)
    ttk.Entry(root, textvariable=numero_parcela, font=font_style).grid(row=12, column=1, pady=2)

    ttk.Label(root, text="Encargos de Inadimplemento:", font=font_style).grid(row=13, column=0, sticky="w")
    opcoes_inadimplemento = [
        ("Juros remuneratórios + Juros de mora 1,00% a.m.", "remuneratorio_mora_a.m"),
        ("Juros remuneratórios + Juros de mora 1,00% a.a.", "remuneratorio_mora_a.a"),
        ("Multa contratual por inadimplemento: 2,00%.", "multa_2_por"),
        ("Comissão de Permanência.", "comissao"),
    ]
    frame_inadimplemento = ttk.Frame(root)
    frame_inadimplemento.grid(row=13, column=1, pady=2, padx=6, sticky="w")
    vars_inadimplemento = {}

    for i, (rotulo, codigo) in enumerate(opcoes_inadimplemento):
        var_inad = tk.BooleanVar(master=root, value=False)
        tk.Checkbutton(
            frame_inadimplemento,
            text=rotulo,
            variable=var_inad,
            font=font_style,
            anchor="w",
            justify="left"
        ).grid(row=i, column=0, sticky="w")
        vars_inadimplemento[codigo] = var_inad

    ttk.Label(root, text="Taxa de mercado:", font=font_style).grid(row=14, column=0, sticky="w")
    tx_mercado = tk.StringVar(master=root, value="Nenhuma")
    serie = [
        "Nenhuma",
        "20769 - PF Crédito rural com taxas de mercado",
        "20770 - PF Crédito rural com taxas reguladas",
        "Taxa limite - 12%"
    ]
    ttk.Combobox(root, values=serie, textvariable=tx_mercado, font=font_style).grid(row=14, column=1, pady=2)

    ttk.Label(root, text="Garantia(s)", font=font_style).grid(row=15, column=0, sticky="w")
    opcoes_garantias = [
        ("Aval", "aval"),
        ("Penhor cedular", "penhor_cedular"),
        ("Hipoteca cedular", "hipoteca_cedular"),
    ]
    frame_garantias = ttk.Frame(root)
    frame_garantias.grid(row=15, column=1, pady=2, padx=6, sticky="w")
    vars_garantias = {}

    for i, (rotulo, codigo) in enumerate(opcoes_garantias):
        var_gar = tk.BooleanVar(master=root, value=False)
        tk.Checkbutton(
            frame_garantias,
            text=rotulo,
            variable=var_gar,
            font=font_style,
            anchor="w",
            justify="left"
        ).grid(row=i, column=0, sticky="w")
        vars_garantias[codigo] = var_gar

    ttk.Label(root, text="Finalidade da operação:", font=font_style).grid(row=16, column=0, sticky="w")
    finalidade_op = tk.StringVar(master=root, value="")
    ttk.Entry(root, textvariable=finalidade_op, font=font_style).grid(row=16, column=1, pady=2)

    existe_cap_var = tk.StringVar(master=root, value="Não")
    ttk.Label(root, text="Há cláusula de capitalização?", font=font_style).grid(row=17, column=0, sticky="w")
    ttk.Combobox(root, values=["Sim", "Não"], textvariable=existe_cap_var, font=font_style).grid(row=17, column=1, pady=2)

    periodicidade_cap_var = tk.StringVar(master=root, value="Não informado")
    ttk.Label(root, text="Periodicidade da capitalização:", font=font_style).grid(row=18, column=0, sticky="w")
    ttk.Combobox(
        root,
        values=["mensal", "anual", "diaria", "semestral", "Não informado"],
        textvariable=periodicidade_cap_var,
        font=font_style
    ).grid(row=18, column=1, pady=2)

    taxa_supera_var = tk.StringVar(master=root, value="Não informado")
    ttk.Label(root, text="Taxa anual > duodécuplo?", font=font_style).grid(row=19, column=0, sticky="w")
    ttk.Combobox(
        root,
        values=["Sim", "Não", "Não informado"],
        textvariable=taxa_supera_var,
        font=font_style
    ).grid(row=19, column=1, pady=2)

    regime_cap_var = tk.StringVar(master=root, value="Não informado")
    ttk.Label(root, text="Regime da capitalização:", font=font_style).grid(row=20, column=0, sticky="w")
    ttk.Combobox(
        root,
        values=["simples", "composto", "omisso", "Não informado"],
        textvariable=regime_cap_var,
        font=font_style
    ).grid(row=20, column=1, pady=2)

    ttk.Button(root, text="Salvar", command=salvar).grid(row=21, column=0, pady=10)
    ttk.Button(root, text="Cancelar", command=cancelar).grid(row=21, column=1, pady=10)

    root.protocol("WM_DELETE_WINDOW", cancelar)

    root.update_idletasks()
    root.geometry("+200+100")
    root.lift()
    root.attributes("-topmost", True)
    root.after(300, lambda: root.attributes("-topmost", False))
    root.focus_force()

    print("AGUARDANDO FECHAMENTO")

    root.mainloop()

    return resultado