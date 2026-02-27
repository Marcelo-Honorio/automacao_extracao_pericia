import re
import PyPDF2
import pandas as pd
from pathlib import Path
import unicodedata

from extrator.regras import carregar_regras

# -----------------------------
# Configuração
# -----------------------------
# REGEX Para data
RE_DATA_LINE = re.compile(r"^\s*(\d{2}[./-]\d{2}[./-]\d{4})\s+(.*)$")
# REGEX para valores monetários
RE_TOK = re.compile(r"(?:(?<=\s)|^)-?\d{1,3}(?:\.\d{3})*,\d{2}(?!\d)(?=(?:\s|$|[)\];:,]))|(?:(?<=\s)|^)-(?:\s|$)")
RE_NUM = re.compile(r"-?\d{1,3}(?:\.\d{3})*,\d{2}$")

# Função uteis para serem utilizadas nas funçãoes principais
def br_to_float(tok: str):
    """'1.234,56' -> 1234.56 ; '-229.362,00' -> -229362.0 ; ''/None/'-' -> None"""
    if tok is None:
        return None
    tok = tok.strip()
    if tok == "" or tok == "-":
        return None
    if not RE_NUM.fullmatch(tok):
        return None
    return float(tok.replace(".", "").replace(",", "."))

def _norm(tok: str) -> str:
    tok = (tok or "").strip()
    return tok

def _is_num(tok: str) -> bool:
    return bool(RE_NUM.match(_norm(tok)))

def _br_to_float(tok: str):
    tok = _norm(tok)
    if not tok or tok == "-" or not _is_num(tok):
        return None
    return float(tok.replace(".", "").replace(",", "."))

def _first_numeric(tokens):
    for i, t in enumerate(tokens):
        if _is_num(t):
            return i, t
    return None, None

def _last_numeric(tokens):
    for t in reversed(tokens):
        if _is_num(t):
            return t
    return None

def adicionar_saldo_calculado(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adiciona colunas:
      - Movimento_num = Debito + Credito
      - Saldo_calc_prev = saldo calculado do período anterior
      - Saldo_calc = acumulado (inicia no débito inicial da 1ª linha útil)
      - Divergencia_saldo (opcional): Saldo_num - Saldo_calc (se Saldo_num existir)
    """
    df = df.copy()

    # Garantir que NaN vira 0 para cálculo "Debito", "Credito"
    deb = pd.to_numeric(df.get("Debito"), errors="coerce").fillna(0.0).abs()
    cre = pd.to_numeric(df.get("Credito"), errors="coerce").fillna(0.0)

    df["Movimento_num"] = deb - cre  # débito já é negativo, crédito positivo

    # Saldo calculado acumulado
    df["Saldo_calculado"] = df["Movimento_num"].cumsum() * -1
  
    # Transforma dados 
    df["Debito"] = deb
    df["Credito"] = cre

    # coluna  'Arquivo'
    colunas = ['Data', 'Historico', 'Debito', 'Credito', 'Saldo', 'Saldo_calculado', 'Pagina', 'Tipo']
    return df.loc[:, colunas]

def normalize_text(s: str) -> str:
    """Remove acentos e padroniza maiúsculas."""
    s = (s or "").strip().upper()
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    return s

# Regras para extratos sem sinal de negativo e positovo nos débitos e créditos
REGRAS = carregar_regras()

HIST_DEBITO = REGRAS["historico_debito"]
HIST_CREDITO = REGRAS["historico_credito"]

# Classificação para extratos sem sinal de negativo e positovo nos débitos e créditos
def classificar_por_historico(historico: str):
    h = normalize_text(historico)

    # crédito primeiro (ex.: "ESTORNO DE JUROS" deve ser crédito)
    for k in HIST_CREDITO:
        if k in h:
            return "CREDITO"

    for k in HIST_DEBITO:
        if k in h:
            return "DEBITO"

    return "INDEFINIDO"

# Fazer as extrações em lote
def extrair_em_lote(pasta_ou_lista):
    """
    Aceita uma pasta (string) ou uma lista de caminhos.
    Retorna DF concatenado.
    """
    paths = []
    if isinstance(pasta_ou_lista, (list, tuple, set)):
        paths = list(pasta_ou_lista)
    else:
        pasta = Path(pasta_ou_lista)
        paths = [str(p) for p in pasta.glob("*.pdf")]

    dfs = []
    for p in paths:
        df = extrair_ficha_grafica_pdf(p)
        dfs.append(df)

    out = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    return out

# Função principal 
def extrair_ficha_grafica_pdf(path_pdf: str) -> pd.DataFrame:
    """
    Extrai linhas de movimento (data no início) de ficha gráfica BB/PJe
    de forma robusta a colunas vazias e linhas de virada (TRANSF. DE SALDO).
    Retorna DF com: Data, Historico, Debito, Credito, Saldo, Saldo_geral, Arquivo, Pagina.
    """
    path_pdf = str(path_pdf)
    rows = []
    sem_mov_num = 0

    with open(path_pdf, "rb") as f:
        reader = PyPDF2.PdfReader(f)

        for page_idx in range(len(reader.pages)):
            texto = reader.pages[page_idx].extract_text() or ""
            for linha in texto.splitlines():
                linha = linha.strip()
                if not linha:
                    continue

                m = RE_DATA_LINE.match(linha)
                if not m:
                    continue

                data = m.group(1).replace("/", ".").replace("-", ".")
                data = data.replace(".", "/")
                resto = m.group(2).strip()

                #tokens = [_norm(t) for t in RE_TOK.findall(resto)]
                tokens = [m.group(0).strip() for m in RE_TOK.finditer(resto)]

                # histórico = remove tokens e normaliza
                historico = RE_TOK.sub("", resto)
                historico = re.sub(r"\s+", " ", historico).strip()
                hist_up = historico.upper()

                mov_idx, mov = _first_numeric(tokens)
                if mov is None:
                    sem_mov_num += 1
                    mov = ""  # mantém linha mesmo assim

                # saldo: token logo após a movimentação, se existir; senão "-"
                saldo = "-"
                if mov_idx is not None and mov_idx + 1 < len(tokens):
                    saldo = tokens[mov_idx + 1]

                # saldo geral: por padrão, último número; senão "-"
                saldo_geral = _last_numeric(tokens) or "-"

                # classifica débito/crédito
                mov_f = _br_to_float(mov)
                debito = mov if (mov_f is not None and mov_f < 0) else ""
                credito = mov if (mov_f is not None and mov_f > 0) else ""

                # Classificação sem credito e debito com sinal
                if mov_f is None:
                    tipo = "INDEFINIDO"

                else:
                    # prioridade 1: sinal colado no número (ou valor numérico negativo/positivo)
                    if mov_f < 0:
                        debito, credito = mov, ""
                        tipo = "DEBITO"
                    elif mov_f > 0:
                        debito, credito = "", mov
                        tipo = "CREDITO"
                    else:
                        tipo = "INDEFINIDO"

                    # prioridade 2: fallback por histórico quando NÃO há sinal na string original
                    # (ex.: "722,99" sem "-" pode ser débito ou crédito dependendo da coluna)
                    if mov and not mov.strip().startswith("-"):
                        tipo_hist = classificar_por_historico(historico)
                        if tipo_hist == "DEBITO":
                            debito, credito = mov, ""
                            tipo = "DEBITO_HIST"
                        elif tipo_hist == "CREDITO":
                            debito, credito = "", mov
                            tipo = "CREDITO_HIST"
                        else:
                            tipo = "INDEFINIDO"
                # REGRA GENÉRICA DE VIRADA: TRANSF. DE SALDO
                # Se saldo/saldo geral vierem como "-" (placeholders), vira 0,00.
                if "TRANSF" in hist_up and "SALDO" in hist_up:
                    if saldo == "-" or saldo == "":
                        saldo = "0,00"
                    # se os dois últimos tokens forem "-" "-" (muito comum), força 0,00
                    if len(tokens) >= 2 and tokens[-1] == "-" and tokens[-2] == "-":
                        saldo_geral = "0,00"
                    if saldo_geral == "-" or saldo_geral == "":
                        saldo_geral = "0,00"

                # opcional: padronizar "-" em vazio para outras linhas
                if saldo == "-":
                    saldo = ""
                if saldo_geral == "-":
                    saldo_geral = ""

                # Colunas numéricas
                debito = br_to_float(debito)
                #if debito < 0:
                #    debito = debito * (-1)
                credito = br_to_float(credito) # positivo
                saldo = br_to_float(saldo)
                saldo_geral = br_to_float(saldo_geral)

                rows.append([
                    data, historico, debito, credito, saldo, saldo_geral,
                    Path(path_pdf).name, page_idx + 1, tipo  # página 1-based
                    ])

    df = pd.DataFrame(rows, columns=[
        "Data", "Historico", "Debito", "Credito", "Saldo", "Saldo_geral", "Arquivo", "Pagina", "Tipo"
        ])
    
    df = adicionar_saldo_calculado(df)

    # auditoria simples (útil em lote)
    df.attrs["linhas_sem_mov_numerica"] = sem_mov_num
    return df
