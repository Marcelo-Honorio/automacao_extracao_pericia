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
    #INSTRUMENTOS,
    PADROES_DATA_CONTRATO,
    PADROES_DATA_VENCIMENTO,
    PADROES_FINALIDADE,
    PADROES_INSTRUMENTO_TITULO
)


class ExtratorContrato:
    def __init__(self, contrato: ContratoPDF):
        self.contrato = contrato
        self.texto = contrato.texto
        self.texto_lower = self.texto.lower()

    def _buscar_primeiro(self, padroes: list[str]):
        for padrao in padroes:
            m = re.search(padrao, self.texto, flags=re.I)
            if m:
                return m.group(1).strip()
        return None

    def _buscar_regex(self, padroes, paginas=3, flags=re.I | re.S):
        """
        Procura o primeiro padrão encontrado nas primeiras páginas do contrato.
        """
        texto = "\n".join(
            pagina.texto for pagina in self.contrato.paginas[:paginas]
        )

        for padrao in padroes:
            m = re.search(padrao, texto, flags)
            if m:
                return m.group(1).strip()

        return None

    def _texto_paginas(self, paginas=2):
        return "\n".join(
            pagina.texto for pagina in self.contrato.paginas[:paginas]
        )
    
    def extrair_numero_contrato(self):
        return self._buscar_primeiro(PADROES_CONTRATO)

    def extrair_valor_liberado(self):
        valor = self._buscar_primeiro(PADROES_VALOR_LIBERADO)
        return valor_br_para_float(valor)

    def extrair_juros_ano(self):
        taxa = self._buscar_primeiro(PADROES_JUROS_ANO)
        return taxa_br_para_float(taxa)

    def extrair_juros_mes(self):
        taxa = self._buscar_primeiro(PADROES_JUROS_MES)
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
        data = self._buscar_regex(PADROES_DATA_CONTRATO, paginas=2)
        return normalizar_data(data) if data else ""

    def extrair_data_vencimento(self):
        data = self._buscar_regex(PADROES_DATA_VENCIMENTO, paginas=8)
        return normalizar_data(data) if data else ""

    def extrair_instrumento(self):
        texto_inicio = self._texto_paginas(paginas=2)

        for padrao, retorno in PADROES_INSTRUMENTO_TITULO:
            if re.search(padrao, texto_inicio, flags=re.I):
                return retorno

        return ""

    def extrair_finalidade(self):
        finalidade = self._buscar_regex(
            PADROES_FINALIDADE,
            paginas=2
        )

        if not finalidade:
            return None

        finalidade = re.sub(r"\s+", " ", finalidade)
        finalidade = finalidade.replace(" - ", " ")
        finalidade = finalidade.strip(" :.;")

        return finalidade

    def extrair_capitalizacao(self):
        existe = any(
            termo in self.texto_lower
            for termo in [
                "capitalização",
                "capitalizacao",
                "juros capitalizados",
                "capitalizados",
                "regime de capitalização",
                "regime de capitalizacao",
            ]
        )

        periodicidade = None

        if "mensal" in self.texto_lower:
            periodicidade = "mensal"
        elif "diária" in self.texto_lower or "diaria" in self.texto_lower:
            periodicidade = "diaria"
        elif "anual" in self.texto_lower:
            periodicidade = "anual"
        elif "semestral" in self.texto_lower:
            periodicidade = "semestral"

        regime = None

        if "juros compostos" in self.texto_lower or "regime composto" in self.texto_lower:
            regime = "composto"
        elif "juros simples" in self.texto_lower or "regime simples" in self.texto_lower:
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


def extrair_parametros_contrato(path_pdf):
    contrato = ContratoPDF(path_pdf)
    extrator = ExtratorContrato(contrato)
    return extrator.to_dict()