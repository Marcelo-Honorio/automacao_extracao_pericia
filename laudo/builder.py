from laudo.formatters import fmt_moeda

# CHAVES E VALORES PARA OS ESTORNOS
ESTORNOS_MAP = {
    "Seguro Penhor": {
        "chave": "seguro_penhor",
        "rotulo": "Seguro Penhor"
    },
    "Seguro de Vida": {
        "chave": "seguro_vida",
        "rotulo": "Seguro de Vida – Produtor Rural"
    },
    "Seguro Agrícola": {
        "chave": "seguro_agricola",
        "rotulo": "Seguro Agrícola"
    },
    "Tarifa": {
        "chave": "tarifa",
        "rotulo": "Tarifa de Estudo de Operações"
    },
    "Juros de Mora": {
        "chave": "juros_mora",
        "rotulo": "Juros de Mora"
    }
}

# Montar os estornos com os valores
def montar_itens_estorno(estornos_selecionados, valores_apurados):
    itens = []

    for nome in estornos_selecionados:
        info = ESTORNOS_MAP.get(nome)
        if not info:
            continue

        valor = valores_apurados.get(info["chave"])
        if valor is None:
            continue

        itens.append({
            "nome": info["rotulo"],
            "valor": fmt_moeda(valor)
        })

    return itens


# transforma os input para utilizar no Laudo
def transformar_input_para_contexto(dados_dict: dict, valores_por_arquivo):
    """
    Transforma:
    {
        "03-Grafico": {...},
        "04-Grafico": {...}
    }

    em:

    {
        "autor": "...",
        "cliente": "...",
        "contratos": [
            {...},
            {...}
        ]
    }
    """
    contratos = []
    substantivo = None
    agente = None
    cliente = None
    continuidade = None

    for nome_arquivo, dados in dados_dict.items():
        if substantivo is None:
            substantivo = dados.get("substantivo", "")        
        if agente is None:
            agente = dados.get("agente", "")
        if cliente is None:
            cliente = dados.get("cliente", "")
        if continuidade is None:
            continuidade = dados.get("agente_continuidade", "")

        valores_apurados = valores_por_arquivo.get(nome_arquivo, {})

        contrato_item = {
            "arquivo": nome_arquivo,
            "contrato": dados.get("contrato", ""),
            "valor_liberado": dados.get("valor_liberado", ""),
            "periodo": dados.get("periodo", ""),
            "estornos": dados.get("estornos", []),
            "juros": dados.get("juros", ""),
            "pasta": dados.get("pasta", ""),
            "valor_parcela": dados.get("valor_parcela", ""),
            "numero_parcela": dados.get("numero_parcela", ""),
            "tx_equivalente": dados.get("tx_equivalente", ""),
            "finalidade_op": dados.get("finalidade_op", ""),
            #"agente_continuidade": dados.get("agente_continuidade", ""),
            "itens": montar_itens_estorno(
                dados.get("estornos", []),
                valores_apurados
            )
        }

        contratos.append(contrato_item)

    return {
        "substantivo": substantivo or "",
        "agente": agente or "",
        "cliente": cliente or "",
        "agente_continuidade": continuidade or "",
        "contratos": contratos
    }
