from __future__ import annotations

import re
from pathlib import Path


PADRAO_ARQUIVO_CONTRATO = re.compile(
    r"(^|[-_\s])contrato([-_\s]|\.|$)",
    flags=re.I
)


def localizar_contrato_pdf(pasta: str | Path) -> Path | None:
    """
    Localiza arquivos como:
    - contrato.pdf
    - 01-contrato.pdf
    - 02 - Contrato - nome.pdf
    - Contrato operação.pdf

    Retorna o primeiro contrato encontrado.
    """

    pasta = Path(pasta)

    if not pasta.exists():
        return None

    candidatos = []

    for arquivo in pasta.glob("*.pdf"):
        nome = arquivo.name.lower()

        if PADRAO_ARQUIVO_CONTRATO.search(nome):
            candidatos.append(arquivo)

    if not candidatos:
        return None

    # Prioriza nomes que começam com número menor, ex: 01-contrato.pdf
    candidatos = sorted(candidatos, key=lambda p: p.name.lower())

    return candidatos[0]