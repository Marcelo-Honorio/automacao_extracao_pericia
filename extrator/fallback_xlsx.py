from __future__ import annotations

import re
from pathlib import Path
import pandas as pd


# Aceita Data como "dd.mm.aaaa", "dd/mm/aaaa" e "dd- mm- aaaa"
RE_DATE = re.compile(r"^\s*(\d{1,2})[./-](\d{1,2})[./-](\d{4})\s*$")


def _norm_col(s: str) -> str:
    """Normaliza nome de coluna para facilitar mapeamento."""
    s = (s or "").strip().lower()
    s = re.sub(r"\s+", " ", s)
    s = s.replace("ç", "c").replace("ã", "a").replace("á", "a").replace("à", "a").replace("â", "a")
    s = s.replace("é", "e").replace("ê", "e").replace("í", "i").replace("ó", "o").replace("ô", "o").replace("ú", "u")
    return s


def _to_date_str(v) -> str:
    """Converte para 'dd.mm.aaaa' (string)."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    if isinstance(v, (pd.Timestamp,)):
        return v.strftime("%d.%m.%Y")

    s = str(v).strip()
    if not s:
        return ""

    m = RE_DATE.match(s)
    if m:
        dd = int(m.group(1))
        mm = int(m.group(2))
        yyyy = int(m.group(3))
        return f"{dd:02d}.{mm:02d}.{yyyy:04d}"

    # tenta parse geral
    try:
        dt = pd.to_datetime(s, dayfirst=True, errors="raise")
        return dt.strftime("%d.%m.%Y")
    except Exception:
        return s  # mantém como está para auditoria


def _br_to_float(v):
    """
    Converte '1.234,56' -> 1234.56 ; '-229.362,00' -> -229362.0
    Aceita também números já numéricos.
    """
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    if isinstance(v, (int, float)):
        return float(v)

    s = str(v).strip()
    if s == "" or s == "-":
        return None

    # remove R$ e espaços
    s = s.replace("R$", "").replace(" ", "")

    # padrão pt-br
    # se vier no formato 1234.56 (ponto decimal), tentamos também
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except Exception:
        return None


def _infer_tipo(debito_num, credito_num, historico: str = "") -> str:
    if debito_num is not None and debito_num != 0:
        return "DEBITO_MANUAL"
    if credito_num is not None and credito_num != 0:
        return "CREDITO_MANUAL"
    return "INDEFINIDO_MANUAL"


def adicionar_saldo_calculado(df: pd.DataFrame) -> pd.DataFrame:
    """Saldo_calc = cumsum(Debito_num + Credito_num)"""
    df = df.copy()
    deb = pd.to_numeric(df.get("Debito_num"), errors="coerce").fillna(0.0)
    cre = pd.to_numeric(df.get("Credito_num"), errors="coerce").fillna(0.0)
    df["Movimento_num"] = deb + cre
    df["Saldo_calc"] = df["Movimento_num"].cumsum()
    df["Saldo_calc_prev"] = df["Saldo_calc"].shift(1).fillna(0.0)
    return df


def ler_ficha_grafica_manual_xlsx(
    path_xlsx: str | Path,
    arquivo_origem: str | None = None,
    pagina: int | None = None,
    sheet: str | int | None = None,
    ) -> pd.DataFrame:
    """
    Lê XLSX manual e padroniza para o mesmo schema do extrator.

    Espera (mínimo) as colunas:
      - Data
      - Historico
      - Debito (ou Debito_num)
      - Credito (ou Credito_num)
    Opcional:
      - Saldo, Saldo_geral

    Retorna DF com:
      Data, Historico, Debito, Credito, Saldo, Saldo_geral,
      Debito_num, Credito_num, Saldo_num, Saldo_geral_num,
      Arquivo, Pagina, Tipo, Fonte ("MANUAL")
      + Saldo_calc, Saldo_calc_prev, Movimento_num
    """
    path_xlsx = Path(path_xlsx)

    # lê tudo como texto para reduzir surpresas; depois converte
    df = pd.read_excel(path_xlsx, sheet_name=sheet if sheet is not None else 0, dtype=str)

    # normaliza nomes de colunas para mapear
    col_map = {c: _norm_col(c) for c in df.columns}

    # candidatos de mapeamento
    def find_col(*names):
        names = set(_norm_col(n) for n in names)
        for orig, norm in col_map.items():
            if norm in names:
                return orig
        return None

    c_data = find_col("data")
    c_hist = find_col("historico", "histórico", "descricao", "descrição", "historico / documento", "historico/documento")
    c_deb = find_col("debito", "débito")
    c_cre = find_col("credito", "crédito")
    c_saldo = find_col("saldo")
    c_sg = find_col("saldo_geral", "saldo geral", "saldo geral ")
    c_deb_num = find_col("debito_num")
    c_cre_num = find_col("credito_num")
    c_saldo_num = find_col("saldo_num")
    c_sg_num = find_col("saldo_geral_num")

    # valida mínimos
    if c_data is None or c_hist is None:
        raise ValueError(f"XLSX manual precisa ter colunas 'Data' e 'Historico'. Arquivo: {path_xlsx.name}")

    # monta base padronizada
    out = pd.DataFrame()
    out["Data"] = df[c_data].map(_to_date_str)
    out["Historico"] = df[c_hist].fillna("").astype(str).str.strip()

    # Debito/Credito texto (se existir)
    out["Debito"] = df[c_deb].fillna("").astype(str).str.strip() if c_deb else ""
    out["Credito"] = df[c_cre].fillna("").astype(str).str.strip() if c_cre else ""

    out["Saldo"] = df[c_saldo].fillna("").astype(str).str.strip() if c_saldo else ""
    out["Saldo_geral"] = df[c_sg].fillna("").astype(str).str.strip() if c_sg else ""

    # numéricos: prioriza *_num se vierem preenchidos
    if c_deb_num:
        out["Debito_num"] = df[c_deb_num].map(_br_to_float)
    else:
        out["Debito_num"] = out["Debito"].map(_br_to_float)

    if c_cre_num:
        out["Credito_num"] = df[c_cre_num].map(_br_to_float)
    else:
        out["Credito_num"] = out["Credito"].map(_br_to_float)

    if c_saldo_num:
        out["Saldo_num"] = df[c_saldo_num].map(_br_to_float)
    else:
        out["Saldo_num"] = out["Saldo"].map(_br_to_float)

    if c_sg_num:
        out["Saldo_geral_num"] = df[c_sg_num].map(_br_to_float)
    else:
        out["Saldo_geral_num"] = out["Saldo_geral"].map(_br_to_float)

    # metadata
    out["Arquivo"] = arquivo_origem if arquivo_origem else path_xlsx.stem
    out["Pagina"] = int(pagina) if pagina is not None else 0
    out["Fonte"] = "MANUAL"

    # tipo
    out["Tipo"] = [
        _infer_tipo(d, c, h) for d, c, h in zip(out["Debito_num"], out["Credito_num"], out["Historico"])
    ]

    # Ordenação por Data mantendo ordem original
    out["_ord"] = range(len(out))
    out["Data_dt"] = pd.to_datetime(out["Data"], format="%d.%m.%Y", errors="coerce")
    out = out.sort_values(["Data_dt", "_ord"]).drop(columns=["_ord"])

    # saldo calculado
    out = adicionar_saldo_calculado(out)

    # limpeza
    out = out.drop(columns=["Data_dt"])

    return out


def tentar_manual_por_pdfstem(manual_dir: str | Path, pdf_path: str | Path) -> Path | None:
    """
    Procura um XLSX manual com o mesmo stem do PDF:
      manual_dir/<pdf.stem>.xlsx
    """
    manual_dir = Path(manual_dir)
    pdf_path = Path(pdf_path)
    cand = manual_dir / f"{pdf_path.stem}.xlsx"
    return cand if cand.exists() else None