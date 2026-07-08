from __future__ import annotations

import re
from pathlib import Path


PADRAO_ARQUIVO_CONTRATO = re.compile(
    r"(^|[-_\s])contrato([-_\s]|\.|$)",
    flags=re.I
)


def localizar_contrato_pdf(pasta: str | Path) -> Path | None:
    pasta = Path(pasta)

    if not pasta.exists():
        return None

    candidatos = [
        arq for arq in pasta.glob("*.pdf")
        if PADRAO_ARQUIVO_CONTRATO.search(arq.name)
    ]

    if not candidatos:
        return None

    return sorted(candidatos, key=lambda p: p.name.lower())[0]