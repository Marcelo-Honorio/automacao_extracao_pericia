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
