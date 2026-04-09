from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from pericia.models import PremissasCapitalizacao


@dataclass(slots=True)
class DecisaoCapitalizacao:
    capitalizacao_valida: bool
    aplicar_regime: Literal["simples", "composto", "afastar"]
    aplicar_estorno_capitalizacao: bool
    fundamentos: list[str] = field(default_factory=list)
    observacoes_laudo: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "capitalizacao_valida": self.capitalizacao_valida,
            "aplicar_regime": self.aplicar_regime,
            "aplicar_estorno_capitalizacao": self.aplicar_estorno_capitalizacao,
            "fundamentos": self.fundamentos,
            "observacoes_laudo": self.observacoes_laudo,
        }


def decidir_capitalizacao(p: PremissasCapitalizacao) -> DecisaoCapitalizacao:
    fundamentos: list[str] = []
    observacoes: list[str] = []

    # 1) Não existe cláusula
    if not p.existe_capitalizacao:
        fundamentos.append("Não foi identificada cláusula expressa de capitalização de juros.")
        observacoes.append("Os encargos devem ser tratados sem capitalização contratualmente pactuada.")
        return DecisaoCapitalizacao(
            capitalizacao_valida=False,
            aplicar_regime="simples",
            aplicar_estorno_capitalizacao=True,
            fundamentos=fundamentos,
            observacoes_laudo=observacoes,
        )

    # 2) Existe cláusula, mas sem periodicidade
    if p.periodicidade_capitalizacao in (None, "omissa"):
        fundamentos.append("Há referência à capitalização, porém sem periodicidade expressa.")
        observacoes.append("A ausência de periodicidade compromete a validade técnica da capitalização.")
        return DecisaoCapitalizacao(
            capitalizacao_valida=False,
            aplicar_regime="simples",
            aplicar_estorno_capitalizacao=True,
            fundamentos=fundamentos,
            observacoes_laudo=observacoes,
        )

    # 3) Existe cláusula e periodicidade, mas o regime está omisso
    if p.regime_capitalizacao in (None, "omisso", "nao_informado"):
        fundamentos.append("O contrato não esclarece se o regime é simples ou composto.")
        observacoes.append("Sem definição do regime, a adoção do método composto fica tecnicamente fragilizada.")
        return DecisaoCapitalizacao(
            capitalizacao_valida=False,
            aplicar_regime="simples",
            aplicar_estorno_capitalizacao=True,
            fundamentos=fundamentos,
            observacoes_laudo=observacoes,
        )

    # 4) Há cláusula, periodicidade e regime.
    # A condição da taxa anual pode reforçar a leitura técnica, mas não precisa ser absoluta.
    if p.regime_capitalizacao == "composto":
        fundamentos.append(
            f"Há cláusula de capitalização com periodicidade {p.periodicidade_capitalizacao} "
            "e indicação de regime composto."
        )
        if p.taxa_anual_supera_duodecuplo is True:
            fundamentos.append(
                "A taxa anual informada é superior ao duodécuplo da taxa mensal, reforçando a leitura de capitalização composta."
            )

        return DecisaoCapitalizacao(
            capitalizacao_valida=True,
            aplicar_regime="composto",
            aplicar_estorno_capitalizacao=False,
            fundamentos=fundamentos,
            observacoes_laudo=observacoes,
        )

    # 5) Regime simples
    fundamentos.append(
        f"Há cláusula de capitalização com periodicidade {p.periodicidade_capitalizacao}, "
        "mas o regime informado é simples/linear."
    )
    return DecisaoCapitalizacao(
        capitalizacao_valida=True,
        aplicar_regime="simples",
        aplicar_estorno_capitalizacao=False,
        fundamentos=fundamentos,
        observacoes_laudo=observacoes,
    )