from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pdfplumber


@dataclass(slots=True)
class PaginaPDF:
    numero: int
    texto: str


class ContratoPDF:
    def __init__(self, path_pdf: str | Path):
        self.path = Path(path_pdf)
        self.paginas: list[PaginaPDF] = self._extrair_paginas()
        self.texto: str = "\n".join(p.texto for p in self.paginas)

    def _extrair_paginas(self) -> list[PaginaPDF]:
        paginas = []

        with pdfplumber.open(self.path) as pdf:
            for numero, pagina in enumerate(pdf.pages, start=1):
                texto = pagina.extract_text() or ""
                paginas.append(PaginaPDF(numero=numero, texto=texto))

        return paginas

    def texto_paginas(self, paginas: int = 3) -> str:
        return "\n".join(p.texto for p in self.paginas[:paginas])

    @property
    def nome_arquivo(self) -> str:
        return self.path.name

    @property
    def stem(self) -> str:
        return self.path.stem

    @property
    def numero_paginas(self) -> int:
        return len(self.paginas)