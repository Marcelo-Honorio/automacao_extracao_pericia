from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional, Literal, Any

# Listas com os tipos de capitalização
PeriodicidadeCapitalizacao = Literal[
    "mensal",
    "anual",
    "diaria",
    "semestral",
    "cobranca_unica",
    "omissa",
]
# Listas com os regimes de capitalização
RegimeCapitalizacao = Literal[
    "simples",
    "composto",
    "omisso",
    "nao_informado",
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

    cliente: str
    agente: str
    contrato: str
    valor_liberado: float
    periodo: str
    estornos: list[str]
    juros: float
    tx_mercado: str
    valor_parcela: float
    numero_parcela: int
    tx_equivalente: str
    finalidade_op: str

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
        cap = data.get("capitalizacao", {}) or {}
        capitalizacao = PremissasCapitalizacao(**cap)

        return cls(
            cliente=data.get("cliente", ""),
            agente=data.get("agente", ""),
            contrato=data.get("contrato", ""),
            valor_liberado=float(data.get("valor_liberado", 0) or 0),
            periodo=data.get("periodo", "mensal"),
            estornos=list(data.get("estornos", [])),
            juros=float(data.get("juros", 0) or 0),
            tx_mercado=data.get("tx_mercado", "Nenhuma"),
            valor_parcela=float(data.get("valor_parcela", 0) or 0),
            numero_parcela=int(data.get("numero_parcela", 0) or 0),
            tx_equivalente=data.get("tx_equivalente", "diaria"),
            finalidade_op=data.get("finalidade_op", ""),
            capitalizacao=capitalizacao,
        )