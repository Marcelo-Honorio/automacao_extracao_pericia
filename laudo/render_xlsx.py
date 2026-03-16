from openpyxl import load_workbook
from copy import copy
from pathlib import Path

# =========================
# CONFIGURAÇÕES
# =========================
BASE_DIR = Path(__file__).resolve().parent
TEMPLATE = BASE_DIR / "templates" / "tamplate_xlsx.xlsx"

SHEET = "ANEXO 2"

START_ROW = 13
TEMPLATE_ROWS = 7


# =========================
# PREENCHER CABEÇALHO
# =========================

def preencher_cabecalho(ws, dados):

    ws["D4"] = dados["juros"]


# =========================
# EXPANDIR TABELA
# =========================

def expandir_tabela(ws, n_linhas):

    if n_linhas > TEMPLATE_ROWS:
        extra = n_linhas - TEMPLATE_ROWS
        ws.insert_rows(START_ROW + TEMPLATE_ROWS, extra)


# =========================
# COPIAR FORMATAÇÃO
# =========================

def copiar_formatacao(ws, n_linhas):

    template_row = START_ROW

    for i in range(n_linhas):

        for col in range(1, 24):

            origem = ws.cell(template_row, col)
            destino = ws.cell(START_ROW + i, col)

            destino._style = copy(origem._style)


# =========================
# PREENCHER TABELA
# =========================

def preencher_tabela(ws, df):

    for i, row in df.iterrows():

        r = START_ROW + i

        ws.cell(r, 1, row["Data"])
        ws.cell(r, 2, row["Historico"])
        ws.cell(r, 3, row["Debito"])
        ws.cell(r, 4, row["Credito"])
        ws.cell(r, 5, row["Saldo"])
        ws.cell(r, 7, row["dias"])
        ws.cell(r, 8, row["dias_acum"])
        ws.cell(r, 9, row["snd"])
        ws.cell(r, 10, row["sna"])
        ws.cell(r, 11, row["snm"])
        ws.cell(r, 12, row["juros"])
        ws.cell(r, 13, row["tx_mensal"])
        ws.cell(r, 14, row["tx_anual"]) ### corrigir p/ incluir tx de mercado
        ws.cell(r, 15, row["Historico"])
        ws.cell(r, 16, row["debito_recal"])
        ws.cell(r, 17, row["estorno_credito"])
        ws.cell(r, 18, row["saldo_recal"])
        ws.cell(r, 19, row["snd"])
        ws.cell(r, 20, row["sna"])
        ws.cell(r, 21, row["snm"])
        ws.cell(r, 22, row["juros_recal"])

# =========================
# PREENCHER RESUMO
# =========================

#def preencher_resumo(ws, resumo):

#    ws["H50"] = resumo["total_juros"]
#    ws["H51"] = resumo["taxa_media"]


# =========================
# FUNÇÃO PRINCIPAL
# =========================

def gerar_relatorio(df, dados_cabecalho):

    wb = load_workbook(TEMPLATE)
    ws = wb[SHEET]

    preencher_cabecalho(ws, dados_cabecalho)

    expandir_tabela(ws, len(df))

    copiar_formatacao(ws, len(df))

    preencher_tabela(ws, df)

    #preencher_resumo(ws, resumo)

    wb.save("relatorio_final.xlsx")
