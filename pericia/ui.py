import tkinter as tk
from tkinter import ttk, messagebox
from pericia.ui_complemento import criar_complemento_garantias, normalizar_data
import re

def create_input_with_options(steam: str, parametros_iniciais=None, parent=None):
    parametros_iniciais = parametros_iniciais or {}
    resultado = {}

    #root = tk.Toplevel()
    root = tk.Toplevel(parent) if parent else tk.Toplevel()
    root.title("Entrada Manual")
    root.resizable(True, True)

    font_style = ("Arial", 12)
    # ===========================================================================================================
    #                                      FUNÇÃO PARA EXTRAIR NÚMERO PROCESSO
    # ===========================================================================================================
    def extrair_numero_processo(nome_arquivo):
        padrao = r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}"

        resultado = re.search(padrao, nome_arquivo)

        if resultado:
            return resultado.group(0)

        return None
    # ===========================================================================================================
    #                                                     SCROLL
    # ===========================================================================================================
    container = ttk.Frame(root)
    container.grid(row=0, column=0, sticky="nsew")

    canvas = tk.Canvas(container)
    scrollbar = ttk.Scrollbar(
        container,
        orient="vertical",
        command=canvas.yview
    )

    scroll_frame = ttk.Frame(canvas)

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas_window = canvas.create_window(
        (0, 0),
        window=scroll_frame,
        anchor="nw"
    )

    canvas.bind(
        "<Configure>",
        lambda e: canvas.itemconfigure(canvas_window, width=e.width)
    )

    canvas.configure(
        yscrollcommand=scrollbar.set
    )

    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)
    # roda do mouse
    canvas.bind_all(
        "<MouseWheel>",
        lambda e: canvas.yview_scroll(
            int(-1 * (e.delta / 120)),
            "units"
        )
    )
    #################################################################################################
    def salvar():
        # Aplicar a função para garantias
        dados_garantias = obter_resultado_garantias()
        # Datas dos contratos e vencimentos
        try:
            data_contrato_fmt = normalizar_data(data_contrato.get())
            data_pagamento_fmt = normalizar_data(data_pagamento.get())
            data_vencimento_fmt = normalizar_data(data_vencimento.get())
        except ValueError as e:
            messagebox.showerror("Erro de data", str(e))
            return

        nonlocal resultado
        resultado = {
            "auto": auto_n.get(),
            "autor": tipo_autor.get(),
            "instrumento": tipo_doc.get(),
            "cliente": nome_cliente.get(),
            "agente": tipo_agente.get(),
            "contrato": contrato_n.get(),
            "valor_liberado": valor_liberado.get(),
            "periodo": periodo_var.get(),
            "estornos": [codigo for codigo, var in vars_estorno.items() if var.get()],
            "juros_ano": juros_ano.get(),
            "juros_mes": juros_mes.get(),
            "tx_mercado": [codigo for codigo, var in vars_tx_mercado.items() if var.get()],
            "valor_parcela": valor_parcela.get(),
            "valor_nominal_parcela": valor_nominal_parcela.get(),
            "numero_parcela": numero_parcela.get(),
            "data_contrato": data_contrato_fmt,
            "data_pagamento": data_pagamento_fmt,
            "data_vencimento": data_vencimento_fmt,
            "tx_equivalente": tx_equivalente_var.get(),
            "opcoes_inadimplento": [codigo for codigo, var in vars_inadimplemento.items() if var.get()],
            "opcoes_garantias": dados_garantias["opcoes_garantias"],
            "complemento_garantias": dados_garantias["complemento_garantias"],
            "finalidade_op": finalidade_op.get("1.0", "end").strip(),
            "aditivo": existe_aditivo.get() == "Sim",
            "Capitalização": {
                "existe_capitalizacao": existe_cap_var.get() == "Sim",
                "periodicidade_capitalizacao": periodicidade_cap_var.get(),
                "taxa_anual_supera_duodecuplo": (
                    True if taxa_supera_var.get() == "Sim"
                    else False if taxa_supera_var.get() == "Não"
                    else taxa_supera_var.get()
                ),
                "regime_capitalizacao": regime_cap_var.get()
            }
        }
        root.quit()
        root.destroy()

    def cancelar():
        root.quit()
        root.destroy()

    ttk.Label(scroll_frame, text=f"Arquivo: {steam}", font=16).grid(row=0, column=0, columnspan=2, pady=5)

    ttk.Label(scroll_frame, text="Autos n°:", font=font_style).grid(row=1, column=0, sticky="w")
    auto_n = extrair_numero_processo(steam)
    auto_n = tk.StringVar(master=scroll_frame, value=parametros_iniciais.get("auto", auto_n))
    ttk.Entry(scroll_frame, textvariable=auto_n, font=font_style).grid(row=1, column=1, pady=2)

    ttk.Label(scroll_frame, text="Autor:", font=font_style).grid(row=2, column=0, sticky="w")
    tipo_autor = tk.StringVar(master=scroll_frame, value=parametros_iniciais.get("autor","Banco do Brasil S.A."))
    ttk.Combobox(
        scroll_frame,
        values=["Banco do Brasil S.A.", "Banco Santander S.A.", "Caixa Econômica Federal", "Banco Bradesco S.A."],
        textvariable=tipo_autor,
        font=font_style
    ).grid(row=2, column=1, pady=2)

    ttk.Label(scroll_frame, text="Tipo operação:", font=font_style).grid(row=3, column=0, sticky="w")
    tipo_doc = tk.StringVar(master=scroll_frame, value=parametros_iniciais.get("instrumento","Cédula Rural Pignoratícia"))
    opcoes_doc = [
        "Cédula Rural Pignoratícia",
        "Cédula Rural Hipotecária",
        "Cédula Rural Pignoratícia e Hipotecária",
        "Nota de Crédito Rural",
        "Cédula de Produto Rural",
        "Cédula de Crédito Bancário"
    ]
    ttk.Combobox(scroll_frame, values=opcoes_doc, textvariable=tipo_doc, font=font_style).grid(row=3, column=1, pady=2)

    ttk.Label(scroll_frame, text="Cliente(s):", font=font_style).grid(row=4, column=0, sticky="w")
    nome_cliente = tk.StringVar(master=scroll_frame, value=parametros_iniciais.get("cliente",""))
    ttk.Entry(scroll_frame, textvariable=nome_cliente, font=font_style).grid(row=4, column=1, pady=2)

    ttk.Label(scroll_frame, text="Agente(s):", font=font_style).grid(row=5, column=0, sticky="w")
    tipo_agente = tk.StringVar(master=scroll_frame, value=parametros_iniciais.get("agente","do réu"))
    ttk.Combobox(
        scroll_frame,
        values=["do réu", "da ré", "dos réus", "das rés"],
        textvariable=tipo_agente,
        font=font_style
    ).grid(row=5, column=1, pady=2)

    ttk.Label(scroll_frame, text="Número da operação:", font=font_style).grid(row=6, column=0, sticky="w")
    contrato_n = tk.StringVar(master=scroll_frame, value=parametros_iniciais.get("contrato","0"))
    ttk.Entry(scroll_frame, textvariable=contrato_n, font=font_style).grid(row=6, column=1, pady=2)

    ttk.Label(scroll_frame, text="Valor liberado/solicitado:", font=font_style).grid(row=7, column=0, sticky="w")
    valor_liberado = tk.DoubleVar(master=scroll_frame, value=parametros_iniciais.get("valor_liberado", 0))
    ttk.Entry(scroll_frame, textvariable=valor_liberado, font=font_style).grid(row=7, column=1, pady=2)

    ttk.Label(scroll_frame, text="Incidência do juros mora:", font=font_style).grid(row=8, column=0, sticky="w")
    periodo_var = tk.StringVar(master=scroll_frame, value=parametros_iniciais.get("periodo","mensal"))
    ttk.Combobox(
        scroll_frame,
        values=["mensal", "cobrança única"],
        textvariable=periodo_var,
        font=font_style
    ).grid(row=8, column=1, pady=2)

    ttk.Label(scroll_frame, text="Estornos:", font=font_style).grid(row=9, column=0, sticky="w")
    opcoes_estorno = [
        ("Seguro Penhor", "seguro_penhor"),
        ("Seguro de Vida", "seguro_vida"),
        ("Seguro Agrícola", "seguro_agricola"),
        ("Juros de Mora", "juros_mora"),
        ("Tarifa", "tarifa"),
    ]
    frame_estorno = ttk.Frame(scroll_frame)
    frame_estorno.grid(row=9, column=1, pady=2, padx=6, sticky="w")
    vars_estorno = {}

    estornos_salvos = parametros_iniciais.get("estornos", [])
    for i, (rotulo, codigo) in enumerate(opcoes_estorno):
        var_estorno = tk.BooleanVar(master=scroll_frame, value=codigo in estornos_salvos)
        tk.Checkbutton(
            frame_estorno,
            text=rotulo,
            variable=var_estorno,
            font=font_style,
            anchor="w",
            justify="left"
        ).grid(row=i, column=0, sticky="w")
        vars_estorno[codigo] = var_estorno

    ttk.Label(scroll_frame, text="Taxa equivalente:", font=font_style).grid(row=10, column=0, sticky="w")
    tx_equivalente_var = tk.StringVar(master=scroll_frame, value=parametros_iniciais.get("tx_equivalente","diaria"))
    ttk.Combobox(
        scroll_frame,
        values=["base30", "diaria"],
        textvariable=tx_equivalente_var,
        font=font_style
    ).grid(row=10, column=1, pady=2)

    ttk.Label(scroll_frame, text="Taxa de juros efetiva (a.a):", font=font_style).grid(row=11, column=0, sticky="w")
    juros_ano = tk.DoubleVar(master=scroll_frame, value=parametros_iniciais.get("juros_ano", 0.00))
    ttk.Entry(scroll_frame, textvariable=juros_ano, font=font_style).grid(row=11, column=1, pady=2)

###########################################################################################################################################
    ttk.Label(scroll_frame, text="Taxa de juros efetiva (a.m):", font=font_style).grid(row=12, column=0, sticky="w")
    juros_mes = tk.DoubleVar(master=scroll_frame, value=parametros_iniciais.get("juros_mes", 0.00))
    ttk.Entry(scroll_frame, textvariable=juros_mes, font=font_style).grid(row=12, column=1, pady=2)

    ttk.Label(scroll_frame, text="Valor da parcela:", font=font_style).grid(row=13, column=0, sticky="w")
    valor_parcela = tk.DoubleVar(master=scroll_frame, value=parametros_iniciais.get("valor_parcela", 0))
    ttk.Entry(scroll_frame, textvariable=valor_parcela, font=font_style).grid(row=13, column=1, pady=2)

###########################################################################################################################################
    ttk.Label(scroll_frame, text="Valor nominal da parcela:", font=font_style).grid(row=14, column=0, sticky="w")
    valor_nominal_parcela = tk.DoubleVar(master=scroll_frame, value=parametros_iniciais.get("valor_nominal_parcela", 0))
    ttk.Entry(scroll_frame, textvariable=valor_nominal_parcela, font=font_style).grid(row=14, column=1, pady=2)

    ttk.Label(scroll_frame, text="Número de parcelas:", font=font_style).grid(row=15, column=0, sticky="w")
    numero_parcela = tk.IntVar(master=scroll_frame, value=parametros_iniciais.get("numero_parcela", 0))
    ttk.Entry(scroll_frame, textvariable=numero_parcela, font=font_style).grid(row=15, column=1, pady=2)

##########################################################################################################################################################
    ttk.Label(scroll_frame, text="Encargos de Inadimplemento:", font=font_style).grid(row=16, column=0, sticky="w")
    opcoes_inadimplemento = [
        ("Juros remuneratórios + Juros de mora 1,00% a.m.", "remuneratorio_mora_a.m"),
        ("Juros remuneratórios + Juros de mora 1,00% a.a.", "remuneratorio_mora_a.a"),
        ("Multa contratual por inadimplemento: 2,00%.", "multa_2_por"),
        ("Comissão de Permanência.", "comissao"),
    ]
    frame_inadimplemento = ttk.Frame(scroll_frame)
    frame_inadimplemento.grid(row=16, column=1, pady=2, padx=6, sticky="w")
    vars_inadimplemento = {}

    inad_salvos = parametros_iniciais.get("opcoes_inadimplento", [])
    for i, (rotulo, codigo) in enumerate(opcoes_inadimplemento):
        var_inad = tk.BooleanVar(master=scroll_frame, value=codigo in inad_salvos)
        tk.Checkbutton(
            frame_inadimplemento,
            text=rotulo,
            variable=var_inad,
            font=font_style,
            anchor="w",
            justify="left"
        ).grid(row=i, column=0, sticky="w")
        vars_inadimplemento[codigo] = var_inad

######################################################################################################################################################     DATAS DE CONTRATO, VENCIMENTOS 
    data_contrato = tk.StringVar(master=scroll_frame, value=parametros_iniciais.get("data_contrato", ""))
    data_pagamento = tk.StringVar(master=scroll_frame, value=parametros_iniciais.get("data_pagamento", ""))
    data_vencimento = tk.StringVar(master=scroll_frame, value=parametros_iniciais.get("data_vencimento", ""))

    ttk.Label(scroll_frame, text="Data da contratação:", font=font_style).grid(row=17, column=0, sticky="w")
    ttk.Entry(scroll_frame, textvariable=data_contrato, font=font_style).grid(row=17, column=1, pady=2)

    ttk.Label(scroll_frame, text="Data do 1ª pagamento:", font=font_style).grid(row=18, column=0, sticky="w")
    ttk.Entry(scroll_frame, textvariable=data_pagamento, font=font_style).grid(row=18, column=1, pady=2)

    ttk.Label(scroll_frame, text="Data de vencimento:", font=font_style).grid(row=19, column=0, sticky="w")
    ttk.Entry(scroll_frame, textvariable=data_vencimento, font=font_style).grid(row=19, column=1, pady=2)

#######################################################################################################################
    ttk.Label(scroll_frame, text="Taxa de mercado:", font=font_style).grid(row=20, column=0, sticky="w")
    tx_mercado = [
        ("Nenhuma", "Nenhuma"),
        ("20769 - PF Crédito rural com taxas de mercado", "20769"),
        ("20770 - PF Crédito rural com taxas reguladas", "20770"),
        ("Taxa limite - 12%", "Taxa limite - 12%"),
    ]
    frame_tx_mercado = ttk.Frame(scroll_frame)
    frame_tx_mercado.grid(row=20, column=1, pady=2, padx=6, sticky="w")
    vars_tx_mercado = {}

    tx_salvos = parametros_iniciais.get("tx_mercado", [])
    for i, (rotulo, codigo) in enumerate(tx_mercado):
        var_mer = tk.BooleanVar(master=scroll_frame, value=codigo in tx_salvos)
        tk.Checkbutton(
            frame_tx_mercado,
            text=rotulo,
            variable=var_mer,
            font=font_style,
            anchor="w",
            justify="left"
        ).grid(row=i, column=0, sticky="w")
        vars_tx_mercado[codigo] = var_mer

    #ttk.Label(scroll_frame, text="Finalidade da operação:", font=font_style).grid(row=20, column=0, sticky="w")
    #finalidade_op = tk.StringVar(master=scroll_frame, value=parametros_iniciais.get("finalidade_op", ""))
    #ttk.Entry(scroll_frame, textvariable=finalidade_op, font=font_style).grid(row=20, column=1, pady=2)
    ttk.Label(scroll_frame, text="Finalidade da operação:", font=font_style).grid(row=21, column=0, sticky="nw")

    finalidade_op = tk.Text(scroll_frame, width=60, height=4, font=font_style)
    finalidade_op.insert("1.0", parametros_iniciais.get("finalidade_op", ""))
    finalidade_op.grid(row=21, column=1, pady=2, padx=6, sticky="w")
############################################################################################################################################################
    ttk.Label(scroll_frame, text="Garantia(s)", font=font_style).grid(row=22, column=0, sticky="w")
    frame_garantias = ttk.Frame(scroll_frame)
    frame_garantias.grid(row=22, column=1, pady=2, padx=6, sticky="w")
    obter_resultado_garantias = criar_complemento_garantias(
        root=root,
        frame_garantias=frame_garantias,
        font_style=font_style,
        parametros_iniciais=parametros_iniciais
    ) 

    existe_aditivo = tk.StringVar(master=scroll_frame, value="Sim" if parametros_iniciais.get("aditivo") else "Não")
    ttk.Label(scroll_frame, text="Existe aditivo?", font=font_style).grid(row=23, column=0, sticky="w")
    ttk.Combobox(scroll_frame, values=["Sim", "Não"], textvariable=existe_aditivo, font=font_style).grid(row=23, column=1, pady=2)

    # parametros salvas de capitalização
    cap = parametros_iniciais.get("Capitalização", {})

    existe_cap_var = tk.StringVar(master=scroll_frame, value="Sim" if cap.get("existe_capitalizacao") else "Não")
    ttk.Label(scroll_frame, text="Há cláusula de capitalização?", font=font_style).grid(row=24, column=0, sticky="w")
    ttk.Combobox(scroll_frame, values=["Sim", "Não"], textvariable=existe_cap_var, font=font_style).grid(row=24, column=1, pady=2)

    periodicidade_cap_var = tk.StringVar(master=scroll_frame, value=cap.get("periodicidade_capitalizacao", "Não informado"))
    ttk.Label(scroll_frame, text="Periodicidade da capitalização:", font=font_style).grid(row=25, column=0, sticky="w")
    ttk.Combobox(
        scroll_frame,
        values=["mensal", "anual", "diaria", "semestral", "Não informado"],
        textvariable=periodicidade_cap_var,
        font=font_style
    ).grid(row=25, column=1, pady=2)

    taxa_supera_var = tk.StringVar(master=scroll_frame, value=cap.get("taxa_anual_supera_duodecuplo", "Não informado"))
    ttk.Label(scroll_frame, text="Taxa anual > duodécuplo?", font=font_style).grid(row=26, column=0, sticky="w")
    ttk.Combobox(
        scroll_frame,
        values=["Sim", "Não", "Não informado"],
        textvariable=taxa_supera_var,
        font=font_style
    ).grid(row=26, column=1, pady=2)

    regime_cap_var = tk.StringVar(master=scroll_frame, value=cap.get("regime_capitalizacao", "Não informado"))
    ttk.Label(scroll_frame, text="Regime da capitalização:", font=font_style).grid(row=27, column=0, sticky="w")
    ttk.Combobox(
        scroll_frame,
        values=["simples", "composto", "omisso", "Não informado"],
        textvariable=regime_cap_var,
        font=font_style
    ).grid(row=27, column=1, pady=2)

    ttk.Button(scroll_frame, text="Salvar", command=salvar).grid(row=28, column=0, pady=10)
    ttk.Button(scroll_frame, text="Cancelar", command=cancelar).grid(row=28, column=1, pady=10)

    root.protocol("WM_DELETE_WINDOW", cancelar)

    root.update_idletasks()
    #950x700+
    root.geometry("750x900+200+100")
    root.lift()
    root.attributes("-topmost", True)
    root.after(300, lambda: root.attributes("-topmost", False))
    root.focus_force()

    print("AGUARDANDO FECHAMENTO")

    root.mainloop()

    return resultado