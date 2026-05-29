from laudo.formatters import fmt_moeda
from laudo.config import OPCOES_ESTORNO, ESTORNOS_MAP

# Função para definir agente de continuidade (agente vem do ui.create_input_with_options())
def agente_continuidade(dados_dict:dict):
    #definir agente de continuidade
    if len(dados_dict.items()) > 1:
        return "das operações celebradas"
    else:
        return "da operação celebrada"

# Função para definir o produtor ou a produtora (agente vem do ui.create_input_with_options())
def definir_produtor(agente:str):
    #Definir a produtor em relação ao agente
    if agente.endswith("réu"):
        return  ["o produtor", "ele", "foi constrangido"]
    elif agente.endswith("ré"):
        return ["a produtora", "ela", "foi constrangida"]
    elif agente.endswith("réus"):
        return ["os produtores", "eles", "foram constrangidos"]
    elif agente.endswith("rés"):
        return ["as produtoras", "elas", "foram constrangidas"]

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

# Função para definir operações e operacão (agente vem do ui.create_input_with_options())
def definir_n_operacao(dados_dict:dict):
    # contar número de contrato
    if len(dados_dict.items()) == 1:
        return ["o contrato", "atende", "na operação", "analisado tem"]
    else:
        return ["os contratos", "atendem", "nas operações", "analisados têm"]

# Função para definir operações com a taxa limite maior que 12%
def definir_operacao_12por(dados_dict:dict):
    # consultar se existe algum contrato para questionar a taxa limite
    operacoes = 0
    for n, d in dados_dict.items():
        if d.get("tx_mercado")=="Taxa limite - 12%":
            operacoes =+ 1
    if operacoes > 1:
        return "as cédulas foram celebradas"
    if operacoes == 1:
        return "a cédula foi celebrada"

# Função para definir os tipos de estornos
def lista_para_texto(lista):
    if not lista:
        return ""
    if len(lista) == 1:
        return lista[0]
    if len(lista) == 2:
        return " e o ".join(lista)
    return ", ".join(lista[:-1]) + " e o " + lista[-1]

def definir_estornos(dados_dict:dict):
    estorno = {}
    lista_estorno = [] 
    for n, d in dados_dict.items():
        for i in d.get("estornos", []):
            if i not in lista_estorno:
                lista_estorno.append(i)
    # mapa código -> nome
    mapa = {codigo: nome for nome, codigo in OPCOES_ESTORNO}

    # ------- SEGURO --------
    flags_seguro = [i.find("seguro")==0 for i in lista_estorno]
    
    if any(flags_seguro):
        lista = [i for i, f in zip(lista_estorno, flags_seguro) if f]
        nomes = [mapa[item] for item in lista if item in mapa]
        estorno["seguro"] = lista_para_texto(nomes)
    
    # ------ TARIFA ----------
    flags_tarifa = [i.find("tarifa")==0 for i in lista_estorno]
    if any(flags_tarifa):
        lista = [i for i, f in zip(lista_estorno, flags_tarifa) if f]
        nomes = [mapa[item] for item in lista if item in mapa]
        estorno["tarifa"] = lista_para_texto(nomes)

    return estorno

# transforma os input para utilizar no Laudo
def transformar_input_para_contexto(dados_dict: dict, valores_por_arquivo):
    import laudo.formatters as f
    
    #quantidade de contratos e operações financeiras
    quant_contrato = definir_n_operacao(dados_dict)
    #operações com a taxa limite maior que 12%
    operacoes_tx_limite = definir_operacao_12por(dados_dict)
    #estornos 
    estornos = definir_estornos(dados_dict)
    # continuidade
    continuidade = agente_continuidade(dados_dict)
    
    contratos = []
    substantivo = None
    agente = None
    cliente = None
    autor = None
    instrumento = None
    
    for nome_arquivo, dados in dados_dict.items():
        #if substantivo is None:
        #    substantivo = dados.get("substantivo", "")        
        if agente is None:
            agente = dados.get("agente", "")
            produtor_a = definir_produtor(dados.get("agente"))
            substantivo= agente.split()[1].capitalize()
        if cliente is None:
            cliente = dados.get("cliente", "")
        if autor is None:
            autor = dados.get("autor", "")
        #    continuidade = dados.get("agente_continuidade", "")
        valores_apurados = valores_por_arquivo.get(nome_arquivo, {})

        # valor para ser utilizado em "valor_parcela"
        v_parcela = dados.get("valor_parcela", "")
        # informações dos contrato
        contrato_item = {
            "arquivo": nome_arquivo,
            "autor": dados.get("autor", ""),
            "instrumento": dados.get("instrumento", ""),
            "contrato": dados.get("contrato", ""),
            "valor_liberado": f.fmt_moeda(dados.get("valor_liberado", "")),
            "periodo": dados.get("periodo", ""),
            "estornos": dados.get("estornos", []),
            "juros": f.fmt_moeda(dados.get("juros", "")),
            "pasta": dados.get("pasta", ""),
            "valor_parcela": v_parcela if v_parcela > 0 else "Não pactuado",
            "numero_parcela": f.fmt_numero(dados.get("numero_parcela", "")),
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
        "autor": autor or "",
        "instrumento": instrumento or "",
        "substantivo": substantivo or "",
        "agente": agente or "",
        "produtor_genero" : { 
            "sujeito": produtor_a[0] or "",
            "pronome": produtor_a[1] or "",
            "verbo_foi": produtor_a[2] or "",
            },
        "cliente": cliente or "",
        "agente_continuidade": continuidade or "",
        "descricao_op_contrato": {
            "quantidade": quant_contrato[0] or "",
            "verbo": quant_contrato[1] or "",
            "quantidade_op": quant_contrato[2] or "",
            "tem": quant_contrato[3] or "",
            },
        "operacao_tx_limite": operacoes_tx_limite or "",
        "estornos": estornos or "",
        "contratos": contratos
    }

#trans_input = transformar_input_para_contexto(parametros_contrato, estornos_por_arquivo)

#lista_estorno = definir_estornos(parametros_contrato)

