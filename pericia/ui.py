import tkinter as tk
from tkinter import ttk

def create_input_with_options(steam: str):
    resultado = {}

    def salvar():
        nonlocal resultado
        resultado = {
            "cliente": nome_cliente.get(),
            "agente": tipo_agente.get(),
            "contrato": contrato_n.get(),
            "valor_liberado": valor_liberado.get(),
            "periodo": periodo_var.get(),
            "estornos": [listbox.get(i) for i in listbox.curselection()],
            "juros": juros_var.get(),
            "tx_mercado": tx_mercado.get(),
            "valor_parcela": valor_parcela.get(),
            "numero_parcela": numero_parcela.get(),
            "tx_equivalente": tx_equivalente_var.get(),
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

    def cancelar():
        root.quit()

    root = tk.Tk()
    root.title("Entrada Manual")
    font_style = ("Arial", 12)

    ttk.Label(root, text=f"Arquivo: {steam}", font=14).grid(row=0, column=0, columnspan=2, pady=5)

    # Janela Nome do cliente
    ttk.Label(root, text="Cliente(s):", font=font_style).grid(row=1, column=0, sticky="w")
    nome_cliente = tk.StringVar(value="")
    nome_cliente_entry = ttk.Entry(root, textvariable=nome_cliente, font=font_style)
    nome_cliente_entry.grid(row=1, column=1, pady=2)
    
    # Janela do autor
    ttk.Label(root, text="Agente(s):", font=font_style).grid(row=2, column=0, sticky="w")
    tipo_agente = tk.StringVar(value="do réu")
    agente_combo = ttk.Combobox(root, values=["do réu", "da ré", "dos réus", "das rés"], textvariable=tipo_agente, font=font_style)
    agente_combo.grid(row=2, column=1, pady=2)

    tk.DoubleVar

    # Janela do numero do contrato
    ttk.Label(root, text="Número da operação:", font=font_style).grid(row=3, column=0, sticky="w")
    contrato_n = tk.StringVar(value="0")
    contrato_entry = ttk.Entry(root, textvariable=contrato_n, font=font_style)
    contrato_entry.grid(row=3, column=1, pady=2) 
    
    # Janela do valor liberado
    ttk.Label(root, text="Valor liberado/solicitado:", font=font_style).grid(row=4, column=0, sticky="w")
    valor_liberado = tk.DoubleVar(value=0)
    valor_liberado_entry = ttk.Entry(root, textvariable=valor_liberado, font=font_style)
    valor_liberado_entry.grid(row=4, column=1, pady=2)
    
    # Janela do periodo
    ttk.Label(root, text="Período:", font=font_style).grid(row=5, column=0, sticky="w")
    periodo_var = tk.StringVar(value="mensal")
    periodo_combo = ttk.Combobox(root, values=["mensal", "cobrança única"], textvariable=periodo_var, font=font_style)
    periodo_combo.grid(row=5, column=1, pady=2)
    
    # Janela do Estorno
    ttk.Label(root, text="Estornos:", font=font_style).grid(row=6, column=0, sticky="w")
    listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, height=4, font=font_style, exportselection=0)
    opcoes_estorno = [
            ("Seguro Penhor",  "seguro_penhor"),
            ("Seguro de Vida", "seguro_vida"),
            ("Seguro Agrícola","seguro_agricola"),
            ("Juros de Mora", "juros_mora"),
            ("Tarifa",         "tarifa"),
        ]
    for rotulo, _codigo in opcoes_estorno:
        listbox.insert(tk.END, rotulo)
    listbox.grid(row=6, column=1, pady=2, padx=6)
    
    # Janela de taxa equivalente
    ttk.Label(root, text="Taxa equivalente:", font=font_style).grid(row=7, column=0, sticky="w")
    tx_equivalente_var = tk.StringVar(value="diaria")
    tx_equivalente_combo = ttk.Combobox(root, values=["base30", "diaria"], textvariable=tx_equivalente_var, font=font_style)
    tx_equivalente_combo.grid(row=7, column=1, pady=2)
    
    # Janela de taxa de juros
    ttk.Label(root, text="Taxa de juros:", font=font_style).grid(row=8, column=0, sticky="w")
    juros_var = tk.DoubleVar(value=0.00)
    juros_entry = ttk.Entry(root, textvariable=juros_var, font=font_style)
    juros_entry.grid(row=8, column=1, pady=2)
    
    # Janela de numero parcela
    ttk.Label(root, text="Valor da parcela:", font=font_style).grid(row=9, column=0, sticky="w")
    valor_parcela = tk.DoubleVar(value=0)
    valor_parcela_entry = ttk.Entry(root, textvariable=valor_parcela, font=font_style)
    valor_parcela_entry.grid(row=9, column=1, pady=2) 

    # Janela de numero parcela
    ttk.Label(root, text="Número de parcelas:", font=font_style).grid(row=10, column=0, sticky="w")
    numero_parcela = tk.IntVar(value=0)
    numero_parcela_entry = ttk.Entry(root, textvariable=numero_parcela, font=font_style)
    numero_parcela_entry.grid(row=10, column=1, pady=2) 

    # Janela finalidade da operação
    ttk.Label(root, text="Finalidade da operação:", font=font_style).grid(row=11, column=0, sticky="w")
    finalidade_op = tk.StringVar(value="")
    finalidade_op_entry = ttk.Entry(root, textvariable=finalidade_op, font=font_style)
    finalidade_op_entry.grid(row=11, column=1, pady=2)

    # Janela de Taxa de mercado
    ttk.Label(root, text="Taxa de mercado:", font=font_style).grid(row=12, column=0, sticky="w")
    tx_mercado = tk.StringVar(value="Nenhuma")
    serie = ["Nenhuma", "20726 - PJ Conta garantida", "20727 - PJ Cheque especial", "20741 - PF Cheque especial", "TMM - PF Conta garantida"]
    tx_mercado_var = ttk.Combobox(root,  values=serie, textvariable=tx_mercado, font=font_style)
    tx_mercado_var.grid(row=12, column=1, pady=2)

    #Existência de capitalização
    existe_cap_var = tk.StringVar(value="Não")
    ttk.Label(root, text="Há cláusula de capitalização?", font=font_style).grid(row=13, column=0, sticky="w")
    ttk.Combobox(root, values=["Sim", "Não"], textvariable=existe_cap_var, font=font_style).grid(row=13, column=1, pady=2)

    #Periodicidade de capitalização
    periodicidade_cap_var = tk.StringVar(value="omissa")
    ttk.Label(root, text="Periodicidade da capitalização:", font=font_style).grid(row=14, column=0, sticky="w")
    ttk.Combobox(
        root,
        values=["mensal", "anual", "diaria", "semestral", "omissa"],
        textvariable=periodicidade_cap_var,
        font=font_style
    ).grid(row=14, column=1, pady=2)

    #Apresentação da taxa de juros
    taxa_supera_var = tk.StringVar(value="Não informado")
    ttk.Label(root, text="Taxa anual > duodécuplo?", font=font_style).grid(row=15, column=0, sticky="w")
    ttk.Combobox(
        root,
        values=["Sim", "Não", "Não informado"],
        textvariable=taxa_supera_var,
        font=font_style
    ).grid(row=15, column=1, pady=2)

    #Regime de capitalização
    regime_cap_var = tk.StringVar(value="nao_informado")
    ttk.Label(root, text="Regime da capitalização:", font=font_style).grid(row=16, column=0, sticky="w")
    ttk.Combobox(
        root,
        values=["simples", "composto", "omisso", "nao_informado"],
        textvariable=regime_cap_var,
        font=font_style
    ).grid(row=16, column=1, pady=2)
    
    # Salvar/Cancelar
    ttk.Button(root, text="Salvar", command=salvar).grid(row=13, column=0, pady=10)
    ttk.Button(root, text="Cancelar", command=cancelar).grid(row=13, column=1, pady=10)
    
    root.mainloop()
    root.destroy()

    return resultado
                        