PADROES_INSTRUMENTO_TITULO = [
    (
        r"\bC[ÉE]DULA\s+RURAL\s+PIGNORAT[IÍ1]CIA\s+E\s+HIPOTEC[ÁA]RIA\b"
        r"|\bCEDULA\s+RURAL\s+PIGNORATICIA\s+E\s+HIPOTECARIA\b",
        "Cédula Rural Pignoratícia e Hipotecária",
    ),
    (
        r"\bC[ÉE]DULA\s+RURAL\s+PIGNORAT[IÍ1]CIA\b"
        r"|\bCEDULA\s+RURAL\s+PIGNORATICIA\b",
        "Cédula Rural Pignoratícia",
    ),
    (
        r"\bC[ÉE]DULA\s+RURAL\s+HIPOTEC[ÁA]RIA\b"
        r"|\bCEDULA\s+RURAL\s+HIPOTECARIA\b",
        "Cédula Rural Hipotecária",
    ),
    (
        r"\bC[ÉE]DULA\s+DE\s+CR[ÉE]DITO\s+BANC[ÁA]RIO\b"
        r"|\bCEDULA\s+DE\s+CREDITO\s+BANCARIO\b",
        "Cédula de Crédito Bancário",
    ),
    (
        r"\bCONTRATO\s+DE\s+ABERTURA\s+DE\s+CR[ÉE]DITO\b"
        r"|\bCONTRATO\s+DE\s+ABERTURA\s+DE\s+CREDITO\b",
        "Contrato de Abertura de Crédito",
    ),
]


PADROES_CONTRATO = [
    r"\bNr\.?\s*[:;]?\s*([0-9]{3}[\.,][0-9]{3}[\.,][0-9]{3})\b",
    r"\bnr\.?\s*[:;]?\s*([0-9]{3}[\.,][0-9]{3}[\.,][0-9]{3})\b",
    r"\b(?:C[ÉE]DULA|CEDULA).*?nr\.?\s*[:;]?\s*([0-9]{3}[\.,][0-9]{3}[\.,][0-9]{3})\b",
    r"\b(?:contrato|opera[çc][ãa]o|operacao|c[ée]dula|cedula)\s*(?:n[ºo.]*)?\s*[:;\-]?\s*([0-9\.\-\/]{5,})",
]


PADROES_VALOR_LIBERADO = [
    r"\bR\$\s*([0-9]{1,3}(?:[\.\s][0-9]{3})*(?:[,\.][0-9]{2}))\b",
    r"\bvalor\s+de\s+R\$\s*([0-9]{1,3}(?:[\.\s][0-9]{3})*(?:[,\.][0-9]{2}))\b",
    r"\bno\s+valor\s+de\s+R\$\s*([0-9]{1,3}(?:[\.\s][0-9]{3})*(?:[,\.][0-9]{2}))\b",
    r"\bquantia\s+de\s+R\$\s*([0-9]{1,3}(?:[\.\s][0-9]{3})*(?:[,\.][0-9]{2}))\b",
    r"\bTOTAL\s*-+\s*R\$\s*([0-9]{1,3}(?:[\.\s][0-9]{3})*(?:[,\.][0-9]{2}))\b",
]


PADROES_JUROS_ANO = [
    # mais comum em Cédulas Rurais
    r"taxa\s+efetiva\s+de\s+([0-9]{1,3}(?:[,.][0-9]+)?)\s*(?:\([^)]*\))?\s*pontos?\s+percentuais\s+ao\s+ano",
    # variação
    r"juros\s+(?:à|a)\s+taxa\s+efetiva\s+de\s+([0-9]{1,3}(?:[,.][0-9]+)?)",
    # apenas "... pontos percentuais ao ano"
    r"([0-9]{1,3}(?:[,.][0-9]+)?)\s*(?:\([^)]*\))?\s*pontos?\s+percentuais\s+ao\s+ano",
    # contratos mais modernos
    r"([0-9]{1,3}(?:[,.][0-9]+)?)\s*%\s*a\.?\s*a\.?",
    # taxa anual
    r"taxa\s+anual\s+de\s+([0-9]{1,3}(?:[,.][0-9]+)?)",
]


PADROES_JUROS_MES = [
    r"([0-9]{1,3}(?:[,.][0-9]+)?)\s*(?:\([^)]*\))?\s*pontos?\s+percentuais\s+ao\s+m[êe]s",
    r"([0-9]{1,3}(?:[,.][0-9]+)?)\s*%\s*a\.?\s*m\.?",
    r"taxa\s+mensal\s+de\s+([0-9]{1,3}(?:[,.][0-9]+)?)",
]

PADROES_BLOCO_ENCARGOS = [
    r"ENCARGOS\s+FINANCEIROS\s*[-–—]?\s*(.+?)(?=CETCR|FORMA\s+DE\s+PAGAMENTO|GARANTIAS|INADIMPLEMENTO|VENCIMENTO|DISPOSIÇÕES|$)"
]

PADROES_DATA_CONTRATO = [
    r"\bA\s+(\d{1,2}\s+de\s+[a-zçãé]+\s+de\s+\d{4})\s+pagarei",
    r"emitida\s+nesta\s+data.*?(\d{2}/\d{2}/\d{4})",
]


PADROES_DATA_VENCIMENTO = [
    r"Venciment[oaº]*\s+(?:em|am)\s+(\d{1,2}\s+de\s+[a-zçãé]+\s+de\s+\d{4})",
    r"vencimento\s+final\s+em\s+(\d{2}/\d{2}/\d{4})",
    r"FORMA\s+DE\s+PAGAMENTO.*?em\s+(\d{2}/\d{2}/\d{4})",
]


PADROES_FINALIDADE = [
    r"destina[\-–—]se\s+ao\s+custeio\s+de[:\s]+(.+?)(?:existente\s+no\s+im[oó]vel|no\s+per[ií]odo|PRODUCAO)",
    r"OR[ÇC]AMENTO\s+DE\s+APLICA[ÇC][ÃA]O\s+DO\s+CR[ÉE]DITO.*?destina[\-–—]se\s+ao\s+custeio\s+de[:\s]+(.+?)(?:existente\s+no\s+im[oó]vel)",
]


PADRAO_DATA = r"\b\d{2}[\/\.\-]\d{2}[\/\.\-]\d{4}\b"