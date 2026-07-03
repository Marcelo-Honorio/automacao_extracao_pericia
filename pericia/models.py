from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional, Literal, Any

# Listas com os tipos de capitalização
PeriodicidadeCapitalizacao = Literal[
    "mensal",
    "anual",
    "diaria",
    "semestral",
    "Não informado",
]
# Listas com os regimes de capitalização
RegimeCapitalizacao = Literal[
    "simples",
    "composto",
    "omisso",
    "Não informado",
]

@dataclass(slots=True)
class PremissasCapitalizacao:
    """
    Representa as premissas técnico-jurídicas ligadas à capitalização.
    Não executa o cálculo; apenas descreve como a cláusula foi lida.
    """
    existe_capitalizacao: bool = False
    periodicidade_capitalizacao: Optional[PeriodicidadeCapitalizacao] = None
    taxa_anual_supera_duodecuplo: Optional[bool] = None
    regime_capitalizacao: Optional[RegimeCapitalizacao] = None
    incluir_explicacao_laudo: bool = True

    def validar(self) -> None:
        """
        Garante consistência lógica das premissas.
        """
        if not self.existe_capitalizacao:
            # Se não existe capitalização, os demais campos não devem forçar leitura positiva
            return

        if self.periodicidade_capitalizacao is None:
            raise ValueError(
                "A periodicidade da capitalização deve ser informada quando houver capitalização."
            )

        if self.regime_capitalizacao is None:
            raise ValueError(
                "O regime da capitalização deve ser informado quando houver capitalização."
            )

    def resumo(self) -> dict[str, Any]:
        return {
            "existe_capitalizacao": self.existe_capitalizacao,
            "periodicidade_capitalizacao": self.periodicidade_capitalizacao,
            "taxa_anual_supera_duodecuplo": self.taxa_anual_supera_duodecuplo,
            "regime_capitalizacao": self.regime_capitalizacao,
            "incluir_explicacao_laudo": self.incluir_explicacao_laudo,
        }


@dataclass(slots=True)
class ParametrosContrato:
    """
    Representa todos os inputs de um contrato/arquivo.
    """
    auto: str
    autor: str
    instrumento: str
    cliente: str
    agente: str
    contrato: str
    valor_liberado: float
    periodo: str
    estornos: list[str]
    juros_ano: float
    juros_mes: float
    tx_mercado: list[str]
    valor_parcela: float
    valor_nominal_parcela: float
    numero_parcela: int
    data_contrato: str
    data_pagamento: str
    data_vencimento: str
    tx_equivalente: str
    opcoes_inadimplento: list[str]
    opcoes_garantias: list[str]
    complemento_garantias: dict
    finalidade_op: str
    aditivo: bool

    capitalizacao: PremissasCapitalizacao = field(default_factory=PremissasCapitalizacao)

    def validar(self) -> None:
        if not self.cliente.strip():
            raise ValueError("O campo 'cliente' é obrigatório.")

        if not self.contrato.strip():
            raise ValueError("O campo 'contrato' é obrigatório.")

        if self.valor_liberado < 0:
            raise ValueError("O valor liberado não pode ser negativo.")

        if self.numero_parcela < 0:
            raise ValueError("O número de parcelas não pode ser negativo.")

        self.capitalizacao.validar()

    def to_dict(self) -> dict[str, Any]:
        """
        Mantém compatibilidade com o restante do projeto,
        caso partes do sistema ainda esperem dicionário.
        """
        data = asdict(self)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ParametrosContrato":
        cap = data.get('Capitalização', {}) or {}
        capitalizacao = PremissasCapitalizacao(**cap)

        return cls(
            auto = data.get("auto", ""),
            autor=data.get("autor", ""),
            instrumento=data.get("instrumento", ""),
            cliente=data.get("cliente", ""),
            agente=data.get("agente", ""),
            contrato=data.get("contrato", ""),
            valor_liberado=float(data.get("valor_liberado", 0) or 0),
            periodo=data.get("periodo", "mensal"),
            estornos=list(data.get("estornos", [])),
            juros_ano=float(data.get("juros_ano", 0) or 0),
            juros_mes=float(data.get("juros_mes", 0) or 0),
            tx_mercado= data.get("tx_mercado", ["Nenhuma"]),
            valor_parcela=float(data.get("valor_parcela", 0) or 0),
            valor_nominal_parcela=float(data.get("valor_nominal_parcela", 0) or 0),
            numero_parcela=int(data.get("numero_parcela", 0) or 0),
            data_contrato=data.get("data_contrato", ""),
            data_pagamento=data.get("data_pagamento", ""),
            data_vencimento=data.get("data_vencimento", ""),
            tx_equivalente=data.get("tx_equivalente", "diaria"),
            opcoes_inadimplento=list(data.get("opcoes_inadimplento", [])),
            opcoes_garantias=list(data.get("opcoes_garantias", [])),
            complemento_garantias=data.get("complemento_garantias", {}),
            finalidade_op=data.get("finalidade_op", ""),
            aditivo=data.get("aditivo", False),
            capitalizacao=capitalizacao,
        )

    ## Extrair dados do contrato
    @classmethod
    def from_pdf(cls, path_pdf) -> "ParametrosContrato":
        from contrato.render import ContratoPDF
        from contrato.extractor import ExtratorContrato

        contrato = ContratoPDF(path_pdf)
        dados = ExtratorContrato(contrato).to_dict()

        defaults = {
            "auto": "",
            "autor": "",
            "cliente": "",
            "agente": "do réu",
            "periodo": "mensal",
            "estornos": [],
            "tx_mercado": ["Nenhuma"],
            "valor_parcela": 0.0,
            "valor_nominal_parcela": 0.0,
            "numero_parcela": 0,
            "data_pagamento": "",
            "tx_equivalente": "diaria",
            "opcoes_inadimplento": [],
            "opcoes_garantias": [],
            "complemento_garantias": {},
            "aditivo": False,
        }

        defaults.update(dados)

        return cls.from_dict(defaults)