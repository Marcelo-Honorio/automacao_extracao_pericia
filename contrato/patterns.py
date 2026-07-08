PADROES_INSTRUMENTO_TITULO = [
    ( 
        r"\bC[ÉE]DULA\s+RURAL\s+PIGNORAT[IÍ1]CIA\s+E\s+HIPOTEC[ÁA]RIA\b", "Cédula Rural Pignoratícia e Hipotecária",
    ),
    (
        r"\bC[ÉE]DULA\s+RURAL\s+PIGNORAT[IÍ1]CIA\b", "Cédula Rural Pignoratícia",
    ),
    (
        r"\bC[ÉE]DULA\s+RURAL\s+HIPOTEC[ÁA]RIA\b", "Cédula Rural Hipotecária",
    ),
    (
        r"\bC[ÉE]DULA\s+DE\s+CR[ÉE]DITO\s+BANC[ÁA]RIO\b", "Cédula de Crédito Bancário",
    ),
    (
        r"\bCONTRATO\s+DE\s+ABERTURA\s+DE\s+CR[ÉE]DITO\b", "Contrato de Abertura de Crédito",
    ),
]

PADROES_CONTRATO = [
    r"\bNr\.?\s*[:;]?\s*([0-9]{3}\.[0-9]{3}\.[0-9]{3})\b",
    r"\bnr\.?\s*[:;]?\s*([0-9]{3}\.[0-9]{3}\.[0-9]{3})\b",
    r"\b(?:C[ÉE]DULA|CEDULA).*?nr\.?\s*[:;]?\s*([0-9]{3}\.[0-9]{3}\.[0-9]{3})\b",
    r"\b(?:contrato|opera[çc][ãa]o|c[ée]dula)\s*(?:n[ºo.]*)?\s*[:;\-]?\s*([0-9\.\-\/]{5,})",
]

PADROES_VALOR_LIBERADO = [
    r"\bR\$\s*([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2})\b",
    r"\bvalor\s+de\s+R\$\s*([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2})\b",
    r"\bno\s+valor\s+de\s+R\$\s*([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2})\b",
    r"\bquantia\s+de\s+R\$\s*([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2})\b",
    r"\bTOTAL\s*-+\s*R\$\s*([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2})\b",
]

PADROES_JUROS_ANO = [
    r"juros\s+(?:à|a)\s+taxa\s+efetiva\s+de\s+([0-9]{1,3}(?:[,.][0-9]+)?)\s*.*?percentuais\s+ao\s+ano",
    r"([0-9]{1,3}(?:[,.][0-9]+)?)\s*%\s*a\.?a\.?",
    r"([0-9]{1,3}(?:[,.][0-9]+)?)\s*pontos?\s+percentuais\s+ao\s+ano",
]

PADROES_JUROS_MES = [
    r"([0-9]{1,3}(?:[,.][0-9]+)?)\s*%\s*a\.?m\.?",
    r"sobretaxa\s+de\s+([0-9]{1,3}(?:[,.][0-9]+)?)\s*%\s*.*?ao\s+m[êe]s",
]

PADROES_DATA_CONTRATO = [
    r"\bA\s+(\d{1,2}\s+de\s+[a-zçãé]+\s+de\s+\d{4})\s+pagarei",
]

PADROES_DATA_VENCIMENTO = [
    r"Venciment[oaº]*\s+(?:em|am)\s+(\d{1,2}\s+de\s+[a-zçãé]+\s+de\s+\d{4})",
    r"vencimento\s+final\s+em\s+(\d{2}/\d{2}/\d{4})",
    r"FORMA\s+DE\s+PAGAMENTO.*?em\s+(\d{2}/\d{2}/\d{4})",
]

PADROES_FINALIDADE = [
    r"destina[\-–]se\s+ao\s+custeio\s+de[:\s]+(.+?)(?:existente\s+no\s+im[oó]vel|no\s+per[ií]odo|PRODUCAO)",
    r"OR[ÇC]AMENTO\s+DE\s+APLICA[ÇC][ÃA]O\s+DO\s+CR[ÉE]DITO.*?destina[\-–]se\s+ao\s+custeio\s+de[:\s]+(.+?)(?:existente\s+no\s+im[oó]vel)",
]

PADRAO_DATA = r"\b\d{2}[\/\.\-]\d{2}[\/\.\-]\d{4}\b"

INSTRUMENTOS = [
    "Cédula Rural Pignoratícia",
    "Cédula Rural Hipotecária",
    "Cédula Rural Pignoratícia e Hipotecária",
    "Cédula de Crédito Bancário",
    "Contrato de Abertura de Crédito",
    "Cédula de Crédito Rural",
    "Nota de Crédito Rural",
]