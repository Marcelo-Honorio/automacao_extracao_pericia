from laudo.formatters import fmt_moeda, fmt_percentual

def montar_contexto_laudo(df, dados_input, resultados_pericia, caminhos_imagens=None):
    caminhos_imagens = caminhos_imagens or {}

    contexto = {
        "autor": dados_input.get("autor", ""),
        "contrato": dados_input.get("contrato", ""),
        "finalidade_op": dados_input.get("finalidade_op", ""),
        "periodo": dados_input.get("periodo", ""),
        "taxa_juros": fmt_percentual(resultados_pericia.get("taxa_juros")),
        "valor_liberado": fmt_moeda(resultados_pericia.get("valor_liberado")),
        "saldo_calculado": fmt_moeda(resultados_pericia.get("saldo_calculado")),
        "saldo_cobrado": fmt_moeda(resultados_pericia.get("saldo_cobrado")),
        "diferenca": fmt_moeda(resultados_pericia.get("diferenca")),
        "conclusao": resultados_pericia.get("conclusao", ""),
        "grafico_saldo": caminhos_imagens.get("grafico_saldo"),
    }
    return contexto


montar_contexto_laudo()
