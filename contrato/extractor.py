from __future__ import annotations

import re
from pathlib import Path

from contrato.render import ContratoPDF
from contrato.normalizer import (
    valor_br_para_float,
    taxa_br_para_float,
    normalizar_data,
)
from contrato.patterns import (
    PADROES_CONTRATO,
    PADROES_VALOR_LIBERADO,
    PADROES_JUROS_ANO,
    PADROES_JUROS_MES,
    PADRAO_DATA,
    PADROES_DATA_CONTRATO,
    PADROES_DATA_VENCIMENTO,
    PADROES_FINALIDADE,
    PADROES_INSTRUMENTO_TITULO,
)


class ExtratorContrato:
    def __init__(self, contrato: ContratoPDF):
        self.contrato = contrato
        self.texto = contrato.texto
        self.texto_lower = self.texto.lower()

    def _texto_paginas(self, paginas=3) -> str:
        return self.contrato.texto_paginas(paginas)

    def _buscar_primeiro(self, padroes: list[str], texto: str | None = None):
        texto = texto or self.texto

        for padrao in padroes:
            m = re.search(padrao, texto, flags=re.I | re.S)

            if m:
                if m.lastindex:
                    return m.group(1).strip()

                return m.group(0).strip()

        return None

    def _buscar_regex(self, padroes: list[str], paginas=3, flags=re.I | re.S):
        texto = self._texto_paginas(paginas)

        return self._buscar_primeiro(padroes, texto=texto)

    def extrair_bloco_encargos(self) -> str:
        m = re.search(
            r"ENCARGOS\s+FINANCEIROS\s*[-–—]?\s*(.+?)(?:CETCR|CUSTO\s+EFETIVO|TARIFA|INADIMPLEMENTO|FORMA\s+DE\s+PAGAMENTO)",
            self.texto,
            flags=re.I | re.S,
        )

        if m:
            return m.group(1)

        return self.texto

    def extrair_instrumento(self):
        texto_inicio = self._texto_paginas(paginas=2)

        for padrao, retorno in PADROES_INSTRUMENTO_TITULO:
            if re.search(padrao, texto_inicio, flags=re.I):
                return retorno

        return ""

    def extrair_numero_contrato(self):
        texto_inicio = self._texto_paginas(paginas=3)

        numero = self._buscar_primeiro(PADROES_CONTRATO, texto_inicio)

        if not numero:
            return ""

        return numero.replace(",", ".")

    def extrair_valor_liberado(self):
        texto_inicio = self._texto_paginas(paginas=3)
        numero = self.extrair_numero_contrato()

        if numero:
            pos = texto_inicio.find(numero)

            if pos == -1:
                pos = texto_inicio.find(numero.replace(".", ","))

            if pos != -1:
                trecho = texto_inicio[pos:pos + 1000]

                m = re.search(
                    r"R\$\s*([0-9]{1,3}(?:[\.\s][0-9]{3})*(?:[,\.][0-9]{2}))",
                    trecho,
                    flags=re.I,
                )

                if m:
                    return valor_br_para_float(m.group(1))

        valor = self._buscar_primeiro(PADROES_VALOR_LIBERADO, texto_inicio)

        return valor_br_para_float(valor)

    def extrair_juros_ano(self):
        texto = self.extrair_bloco_encargos()
        taxa = self._buscar_primeiro(PADROES_JUROS_ANO, texto)

        if taxa is None:
            taxa = self._buscar_primeiro(PADROES_JUROS_ANO, self.texto)

        return taxa_br_para_float(taxa)

    def extrair_juros_mes(self):
        texto = self.extrair_bloco_encargos()
        taxa = self._buscar_primeiro(PADROES_JUROS_MES, texto)

        if taxa is None:
            taxa = self._buscar_primeiro(PADROES_JUROS_MES, self.texto)

        return taxa_br_para_float(taxa)

    def extrair_datas(self):
        datas = re.findall(PADRAO_DATA, self.texto)

        datas = [normalizar_data(d) for d in datas]

        return {
            "data_contrato": datas[0] if len(datas) >= 1 else "",
            "data_pagamento": datas[1] if len(datas) >= 2 else "",
            "data_vencimento": datas[-1] if datas else "",
        }

    def extrair_data_contrato(self):
        data = self._buscar_regex(PADROES_DATA_CONTRATO, paginas=3)
        return normalizar_data(data) if data else ""

    def extrair_data_vencimento(self):
        data = self._buscar_regex(PADROES_DATA_VENCIMENTO, paginas=8)
        return normalizar_data(data) if data else ""

    def extrair_finalidade(self):
        finalidade = self._buscar_regex(PADROES_FINALIDADE, paginas=3)

        if not finalidade:
            return ""

        finalidade = re.sub(r"\s+", " ", finalidade)
        finalidade = finalidade.replace(" - ", " ")
        finalidade = finalidade.replace("—", " ")
        finalidade = finalidade.strip(" :.;")

        return finalidade

    def extrair_capitalizacao(self):
        texto = self.extrair_bloco_encargos()
        texto_lower = texto.lower()

        existe = any(
            termo in texto_lower
            for termo in [
                "capitalização",
                "capitalizacao",
                "capitalizados",
                "juros capitalizados",
                "regime de capitalização",
                "regime de capitalizacao",
            ]
        )

        periodicidade = None

        if "capitalizados mensalmente" in texto_lower or "capitalização mensal" in texto_lower:
            periodicidade = "mensal"
        elif "capitalizados diariamente" in texto_lower or "capitalização diária" in texto_lower:
            periodicidade = "diaria"
        elif "capitalizados anualmente" in texto_lower or "capitalização anual" in texto_lower:
            periodicidade = "anual"
        elif "capitalizados semestralmente" in texto_lower or "capitalização semestral" in texto_lower:
            periodicidade = "semestral"

        regime = None

        if "juros compostos" in texto_lower or "regime composto" in texto_lower:
            regime = "composto"
        elif "juros simples" in texto_lower or "regime simples" in texto_lower:
            regime = "simples"
        elif existe:
            regime = "nao_informado"

        return {
            "existe_capitalizacao": existe,
            "periodicidade_capitalizacao": periodicidade,
            "taxa_anual_supera_duodecuplo": None,
            "regime_capitalizacao": regime,
        }

    def extrair_campos(self) -> dict:
        juros_ano = self.extrair_juros_ano() or 0.0
        juros_mes = self.extrair_juros_mes() or 0.0

        return {
            "instrumento": self.extrair_instrumento() or "",
            "contrato": self.extrair_numero_contrato() or "",
            "valor_liberado": self.extrair_valor_liberado() or 0.0,
            "data_contrato": self.extrair_data_contrato() or "",
            "data_vencimento": self.extrair_data_vencimento() or "",
            "finalidade_op": self.extrair_finalidade() or "",
            "juros_ano": juros_ano,
            "juros_mes": juros_mes,
            "capitalizacao": self.extrair_capitalizacao(),
        }

    def to_dict(self) -> dict:
        return self.extrair_campos()


def extrair_parametros_contrato(path_pdf: str | Path):
    contrato = ContratoPDF(path_pdf)
    extrator = ExtratorContrato(contrato)
    return extrator.to_dict()