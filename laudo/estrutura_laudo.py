from dataclasses import dataclass
from typing import Callable


@dataclass
class SecaoLaudo:
    id: str
    titulo: str
    bloco: str
    ordem: int
    sempre_incluir: bool = False


@dataclass
class Irregularidade:
    id: str
    titulo: str
    secao: str
    subtitulo: str
    bloco: str
    ordem: int
    regra: Callable[[dict], bool]

# Seções do laudo
SECOES = {
    "carencia_fluxo": {
        "titulo": "Carência e fluxo contratual",
        "bloco": "secao_carencia_fluxo",
        "ordem": 10,
    },
    "encadeamento": {
        "titulo": "Encadeamento das operações",
        "bloco": "secao_encadeamento",
        "ordem": 20,
    },
    "encargos_remuneratorios": {
        "titulo": "Encargos remuneratórios",
        "bloco": "secao_encargos_remuneratorios",
        "ordem": 30,
    },
    "capitalizacao": {
        "titulo": "Capitalização de juros",
        "bloco": "secao_capitalizacao",
        "ordem": 40,
    },
    "cobrancas_acessorias": {
        "titulo": "Cobranças acessórias",
        "bloco": "secao_cobrancas_acessorias",
        "ordem": 50,
    },
    "inadimplemento": {
        "titulo": "Encargos de inadimplemento",
        "bloco": "secao_inadimplemento",
        "ordem": 60,
    },
}

def normalizar_texto(valor):
    if valor is None:
        return ""
    return str(valor).strip().lower()

def gerar_decisoes_periciais(dados: dict) -> dict:
    # lista unica de estornos
    estornos = list({
            estorno
            for valores in dados.values()
            for estorno in valores.get("estornos", [])
    })

    dados = dados.values()
    capitalizacao = dados.get("capitalizacao", {})

    inadimplemento = dados.get("opcoes_inadimplento", []) or []

    #tx_mercado = normalizar_texto(dados.get("tx_mercado"))
    periodo_capitalizacao = normalizar_texto(
        capitalizacao.get("periodicidade_capitalizacao")
    )
    regime_capitalizacao = normalizar_texto(
        capitalizacao.get("regime_capitalizacao")
    )

    existe_capitalizacao = capitalizacao.get("existe_capitalizacao") is True

    # Decisão de taxa utilizada
    decisao_tx = dados.get("taxa_utilizada", {})
    tx_mercado = []
    tx_mercado.extend([decisao_tx.get("codigo")])
    tx_mercado.extend([decisao_tx.get("criterio")])
    
    return {
        # Futuro — por enquanto sempre falso
        "juros_carencia_sem_datas_claras": False,
        "encadeamento_operacoes": False,
        "cdi_com_substituicao_indevida": False,
        "cdi_como_encargo_remuneratorio": False,
        "capitalizacao_anual_sem_pactuacao": False,

        # Encargos remuneratórios
        "taxa_superior_media_mercado": sum(["20769" in i for i in tx_mercado])>0,
        "juros_superiores_plano_safra": sum([("20769" in i or "20770" in i) for i in tx_mercado])>0,
        "juros_superiores_12_aa_credito_rural": sum([('Taxa limite - 12%' in i or "TL" in i) for i in tx_mercado])>0,

        # Resultado da perícia — alimentar futuramente por cálculo
        "taxa_superior_contrato_originario": dados.get("juros_superior_contrato_originario") is True,

        # Capitalização
        "capitalizacao_sem_pactuacao": (
            existe_capitalizacao is not True
            or periodo_capitalizacao in {"", "não informado", "nao informado"}
            or regime_capitalizacao in {"", "não informado", "nao informado"}
        ),

        "periodicidade_capitalizacao_rural": (
            periodo_capitalizacao != "semestral"
            and periodo_capitalizacao != ""
        ),

        # Estornos
        "cobranca_indevida_seguros_tarifa": len(estornos) > 0,

        # Inadimplemento
        "inadimplemento_ilegal_oneroso": (
            "remuneratorio_mora_a.m" in inadimplemento
            or (existe_capitalizacao is not True 
                or periodo_capitalizacao in {"", "não informado", "nao informado"} 
                or regime_capitalizacao in {"", "não informado", "nao informado"}
                ) is True
            or dados.get("juros_superior_taxa_limite_ou_mercado") is True
        ),
    }

# catalogo de irregularidades
IRREGULARIDADES = {
    "juros_carencia_sem_datas_claras": Irregularidade(
        id="juros_carencia_sem_datas_claras",
        titulo="Ausência de clara e expressa pactuação das datas de pagamento dos juros de carência",
        secao="carencia_fluxo",
        subtitulo="Datas de pagamento dos juros de carência",
        bloco="irr_juros_carencia_sem_datas_claras",
        ordem=10,
        regra=lambda d: d["juros_carencia_sem_datas_claras"],
        ),

    "encadeamento_operacoes": Irregularidade(
        id="encadeamento_operacoes",
        titulo="Encadeamento das operações",
        secao="encadeamento",
        subtitulo="Encadeamento das operações",
        bloco="irr_encadeamento_operacoes",
        ordem=10,
        regra=lambda d: d["encadeamento_operacoes"],
        ),

    "taxa_superior_media_mercado": Irregularidade(
        id="taxa_superior_media_mercado",
        titulo="Onerosidade excessiva: Taxa de Juros Superior às Taxas de Juros Médias de Mercado",
        secao="encargos_remuneratorios",
        subtitulo="Taxa de juros superior à média de mercado",
        bloco="irr_taxa_superior_media_mercado",
        ordem=10,
        regra=lambda d: d["taxa_superior_media_mercado"],
        ),

    "juros_superiores_plano_safra": Irregularidade(
        id="juros_superiores_plano_safra",
        titulo="Onerosidade excessiva: Juros remuneratórios superiores à taxa fixada no Plano Safra",
        secao="encargos_remuneratorios",
        subtitulo="Juros remuneratórios superiores à taxa fixada no Plano Safra",
        bloco="irr_juros_superiores_plano_safra",
        ordem=20,
        regra=lambda d: d["juros_superiores_plano_safra"],
        ),

    "juros_superiores_12_aa_credito_rural": Irregularidade(
        id="juros_superiores_12_aa_credito_rural",
        titulo="Juros remuneratórios superiores à taxa de 12,00% a.a. para operações de crédito rural",
        secao="encargos_remuneratorios",
        subtitulo="Juros remuneratórios superiores a 12,00% a.a.",
        bloco="irr_juros_superiores_12_aa_credito_rural",
        ordem=30,
        regra=lambda d: d["juros_superiores_12_aa_credito_rural"],
        ),

    "cdi_com_substituicao_indevida": Irregularidade(
        id="cdi_com_substituicao_indevida",
        titulo="Ilegalidade e Onerosidade excessiva: Utilização de CDI como encargo remuneratório e substituição indevida pelo Média/INPC/IGP-M (FGV)",
        secao="encargos_remuneratorios",
        subtitulo="Utilização de CDI como encargo remuneratório e substituição indevida de índice",
        bloco="irr_cdi_com_substituicao_indevida",
        ordem=40,
        regra=lambda d: d["cdi_com_substituicao_indevida"],
        ),

    "cdi_como_encargo_remuneratorio": Irregularidade(
        id="cdi_como_encargo_remuneratorio",
        titulo="Ilegalidade e Onerosidade excessiva: Utilização de CDI como encargo remuneratório",
        secao="encargos_remuneratorios",
        subtitulo="Utilização de CDI como encargo remuneratório",
        bloco="irr_cdi_como_encargo_remuneratorio",
        ordem=50,
        regra=lambda d: d["cdi_como_encargo_remuneratorio"],
        ),

    "taxa_superior_contrato_originario": Irregularidade(
        id="taxa_superior_contrato_originario",
        titulo="Onerosidade excessiva: Taxa de juros superior ao contrato originário",
        secao="encargos_remuneratorios",
        subtitulo="Taxa de juros superior ao contrato originário",
        bloco="irr_taxa_superior_contrato_originario",
        ordem=60,
        regra=lambda d: d["taxa_superior_contrato_originario"],
        ),

    "capitalizacao_sem_pactuacao": Irregularidade(
        id="capitalizacao_sem_pactuacao",
        titulo="Capitalização de juros sem expressa pactuação (anatocismo)",
        secao="capitalizacao",
        subtitulo="Capitalização de juros sem expressa pactuação",
        bloco="irr_capitalizacao_sem_pactuacao",
        ordem=10,
        regra=lambda d: d["capitalizacao_sem_pactuacao"],
        ),

    "periodicidade_capitalizacao_rural": Irregularidade(
        id="periodicidade_capitalizacao_rural",
        titulo="Periodicidade da capitalização para contratos rurais e anatocismo",
        secao="capitalizacao",
        subtitulo="Periodicidade da capitalização em contratos rurais",
        bloco="irr_periodicidade_capitalizacao_rural",
        ordem=20,
        regra=lambda d: d["periodicidade_capitalizacao_rural"],
        ),

    "capitalizacao_anual_sem_pactuacao": Irregularidade(
        id="capitalizacao_anual_sem_pactuacao",
        titulo="Capitalização de juros com periodicidade anual sem expressa pactuação",
        secao="capitalizacao",
        subtitulo="Capitalização anual sem expressa pactuação",
        bloco="irr_capitalizacao_anual_sem_pactuacao",
        ordem=30,
        regra=lambda d: d["capitalizacao_anual_sem_pactuacao"],
        ),

    "cobranca_indevida_seguros_tarifa": Irregularidade(
        id="cobranca_indevida_seguros_tarifa",
        titulo="Cobrança indevida de Seguros e Tarifa",
        secao="cobrancas_acessorias",
        subtitulo="Cobrança indevida de seguros e tarifa",
        bloco="irr_cobranca_indevida_seguros_tarifa",
        ordem=10,
        regra=lambda d: d["cobranca_indevida_seguros_tarifa"],
        ),

    "inadimplemento_ilegal_oneroso": Irregularidade(
        id="inadimplemento_ilegal_oneroso",
        titulo="Encargos de inadimplemento - Ilegalidade e Onerosidade excessiva",
        secao="inadimplemento",
        subtitulo="Encargos de inadimplemento",
        bloco="irr_inadimplemento_ilegal_oneroso",
        ordem=10,
        regra=lambda d: d["inadimplemento_ilegal_oneroso"],
        ),
}

# Funções para montar estrutura
def identificar_irregularidades(decisoes: dict) -> list[Irregularidade]:
    itens = []

    for irr in IRREGULARIDADES.values():
        if irr.regra(decisoes):
            itens.append(irr)

    return sorted(
        itens,
        key=lambda irr: (SECOES[irr.secao]["ordem"], irr.ordem)
    )


def montar_estrutura_laudo(dados: dict) -> dict:
    decisoes = gerar_decisoes_periciais(dados)
    irregularidades = identificar_irregularidades(decisoes)

    estrutura = {}

    for irr in irregularidades:
        secao_meta = SECOES[irr.secao]

        if irr.secao not in estrutura:
            estrutura[irr.secao] = {
                "id": irr.secao,
                "titulo": secao_meta["titulo"],
                "bloco": secao_meta["bloco"],
                "ordem": secao_meta["ordem"],
                "itens": [],
            }

        estrutura[irr.secao]["itens"].append({
            "id": irr.id,
            "titulo": irr.titulo,
            "subtitulo": irr.subtitulo,
            "bloco": irr.bloco,
            "ordem": irr.ordem,
        })

    return dict(sorted(estrutura.items(), key=lambda x: x[1]["ordem"]))


def montar_blocos_ativos(dados: dict) -> dict:
    estrutura = montar_estrutura_laudo(dados)

    blocos = {}

    for secao in estrutura.values():
        blocos[secao["bloco"]] = True

        for item in secao["itens"]:
            blocos[item["bloco"]] = True

    return blocos

# Montar dicionario de estornos no contrato (estornos_selecionados =  lista de estornos)
def gerar_flags_estornos(dados_dict:dict):
    #criar a lisa de estornos
    lista_estorno = []
    for n, d in dados_dict.items():
        for i in d.get("estornos", []):
            if i not in lista_estorno:
                lista_estorno.append(i)
    # Possiveis estornos
    todos = [
        "seguro_penhor",
        "seguro_vida",
        "seguro_agricola",
        "juros_mora",
        "tarifa",
    ]
    
    return {item: item in lista_estorno for item in todos}

def montar_sumario_dinamico(dados: dict) -> list[dict]:
    estrutura = montar_estrutura_laudo(dados)

    sumario = []
    numero_secao = 1

    for secao in estrutura.values():
        secao_sumario = {
            "numero": numero_secao,
            "titulo": secao["titulo"],
            "itens": [],
        }

        numero_item = 1

        for item in secao["itens"]:
            secao_sumario["itens"].append({
                "numero": f"{numero_secao}.{numero_item}",
                "titulo": item["subtitulo"],
                "bloco": item["bloco"],
            })
            numero_item += 1

        sumario.append(secao_sumario)
        numero_secao += 1

    return sumario

def gerar_decisoes_irregularidade(dados_dict:dict):
    # Irregularidades principais
    decisoes_irregularidades = gerar_decisoes_periciais(dados_dict)
    # Subdecisões
    subdecisoes_estornos = gerar_flags_estornos(dados_dict)
    # Concatenar as subdecisões quando a decisão principal se estiver ativa
    if decisoes_irregularidades.get("cobranca_indevida_seguros_tarifa"):
        decisoes_irregularidades = {
            **decisoes_irregularidades,
            **subdecisoes_estornos,
        }
    return decisoes_irregularidades