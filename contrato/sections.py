from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(slots=True)
class SecaoContrato:
    titulo: str
    texto: str
    pagina_inicio: int | None = None
    pagina_fim: int | None = None


def normalizar_texto_busca(texto: str) -> str:
    texto = texto or ""
    texto = texto.upper()

    mapa = str.maketrans(
        "ÁÀÂÃÉÊÍÓÔÕÚÇ",
        "AAAAEEIOOOUC"
    )

    texto = texto.translate(mapa)
    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def parece_titulo(linha: str) -> bool:
    linha = linha.strip()

    if not linha:
        return False

    linha_norm = normalizar_texto_busca(linha)

    if len(linha_norm) < 5:
        return False

    padroes_titulo = [
        r"^CLAUSULA\s+[A-Z0-9]+",
        r"^[0-9]+\s*[-–.)]\s+[A-Z]",
        r"^[IVXLCDM]+\s*[-–.)]\s+[A-Z]",
        r"^[A-Z0-9\s\-–/]{8,}$",
    ]

    return any(re.match(p, linha_norm) for p in padroes_titulo)


def dividir_em_secoes(paginas) -> list[SecaoContrato]:
    secoes = []

    titulo_atual = "INICIO"
    texto_atual = []
    pagina_inicio = None
    pagina_fim = None

    for pagina in paginas:
        numero_pagina = pagina.numero
        linhas = pagina.texto.splitlines()

        for linha in linhas:
            linha_limpa = linha.strip()

            if parece_titulo(linha_limpa):
                if texto_atual:
                    secoes.append(
                        SecaoContrato(
                            titulo=titulo_atual,
                            texto="\n".join(texto_atual).strip(),
                            pagina_inicio=pagina_inicio,
                            pagina_fim=pagina_fim,
                        )
                    )

                titulo_atual = linha_limpa
                texto_atual = []
                pagina_inicio = numero_pagina
                pagina_fim = numero_pagina
            else:
                texto_atual.append(linha)
                if pagina_inicio is None:
                    pagina_inicio = numero_pagina
                pagina_fim = numero_pagina

    if texto_atual:
        secoes.append(
            SecaoContrato(
                titulo=titulo_atual,
                texto="\n".join(texto_atual).strip(),
                pagina_inicio=pagina_inicio,
                pagina_fim=pagina_fim,
            )
        )

    return secoes


def localizar_secao(secoes: list[SecaoContrato], palavras: list[str]) -> SecaoContrato | None:
    palavras_norm = [normalizar_texto_busca(p) for p in palavras]

    melhor_secao = None
    melhor_pontuacao = 0

    for secao in secoes:
        titulo = normalizar_texto_busca(secao.titulo)
        texto = normalizar_texto_busca(secao.texto)

        pontuacao = 0

        for palavra in palavras_norm:
            if palavra in titulo:
                pontuacao += 3
            if palavra in texto:
                pontuacao += 1

        if pontuacao > melhor_pontuacao:
            melhor_pontuacao = pontuacao
            melhor_secao = secao

    return melhor_secao