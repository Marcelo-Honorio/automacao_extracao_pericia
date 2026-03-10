from laudo.formatters import fmt_moeda, fmt_percentual

def montar_contexto_laudo(df, dados_input, resultados_pericia, caminhos_imagens=None):
    caminhos_imagens = caminhos_imagens or {}

    '''ex: dados_input
    {'cliente': 'Marcelo Honorio',
    'agente': 'do réu',
    'contrato': '123456',
    'periodo': 'mensal',
    'estornos': ['Seguro Penhor', 'Seguro de Vida'],
    'juros': '12',
    'pasta': 'NovaPasta',
    'valor_parcela': '12000',
    'numero_parcela': '5',
    'tx_equivalente': 'diaria',
    'finalidade_op': 'Custeio'}
    '''
    return contexto

path_pdf = "C:\\Users\\marce\\Downloads\\PDF\\03-Ficha Grafica.pdf"

with open(path_pdf, "rb") as f:
    reader = PyPDF2.PdfReader(f)

    for page_idx in range(len(reader.pages)):
        texto = reader.pages[page_idx].extract_text() or ""


import camelot
import pandas as pd

tables = camelot.read_pdf(
    path_pdf,
    pages="all"
)

print(tables)

df = tables[0].df
print(df)

tables = camelot.read_pdf(
    path_pdf,
    pages="1",
    flavor="stream",
    row_tol=10,
    column_tol=10
)
df = tables[0].df
print(df)

# limpar colunas
df = df.loc[:, df.columns != ""]
df = df.loc[:, ~df.columns.duplicated()]

