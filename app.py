from pathlib import Path
#from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox

def validar_df_basico(df):
    """
    Validação simples e genérica:
      - OK: sem indefinidos
      - REVISAR: tem indefinidos, mas tem linhas suficientes
      - FALHA: vazio ou quase nada útil
    """
    if df is None or df.empty:
        return "FALHA", ["DF vazio"]

    # mínimo de linhas
    if len(df) < 3:
        return "FALHA", [f"Poucas linhas: {len(df)}"]

    motivos = []

    if "Tipo" in df.columns:
        indef = (df["Tipo"] == "INDEFINIDO").sum()
        if indef > 0:
            motivos.append(f"Linhas INDEFINIDO: {indef}")

            # regra simples: se mais de 20% indefinido -> REVISAR
            if indef / max(len(df), 1) >= 0.20:
                return "REVISAR", motivos
            return "REVISAR", motivos

    return "OK", motivos

def gerar_template_manual_xlsx(path_out: Path):
    """
    Gera um template simples para preenchimento manual.
    """
    import pandas as pd
    cols = ["Data", "Historico", "Debito", "Credito", "Saldo", "Saldo_geral"]
    df = pd.DataFrame(columns=cols)
    df.to_excel(path_out, index=False)


def processar_pasta(pasta: Path, out_root: Path):
    # bibliotecas
    import pandas as pd
    from extrator.logging_utils import setup_logger
    from extrator.io_utils import salvar_resultados
    from extrator.ficha_grafica import extrair_ficha_grafica_pdf  # sua função atual
    from extrator.fallback_xlsx import tentar_manual_por_pdfstem, ler_ficha_grafica_manual_xlsx

    out_dir = out_root
    (out_dir / "logs").mkdir(parents=True, exist_ok=True)
    logger = setup_logger(out_dir / "logs")

    logger.info(f"Iniciando processamento da pasta: {pasta}")
    pdfs = sorted([p for p in pasta.glob("*.pdf")])
    if not pdfs:
        raise RuntimeError("Nenhum PDF com 'Ficha Grafica' no nome foi encontrado na pasta.")

    dfs = []
    erros = []

    for pdf in pdfs:
        try:
            logger.info(f"Processando: {pdf.name}")
            df = extrair_ficha_grafica_pdf(str(pdf))
            # salva 1 EXCEL por PDF
            out_xlsx = out_dir / f"{pdf.stem}.xlsx"
            df.to_excel(out_xlsx, index=False)
            logger.info(f"Planilha gerada: {out_xlsx.name}")
            
            # Concatenando dados
            dfs.append(df)
        except Exception as e:
            logger.exception(f"Erro em {pdf.name}: {e}")
            erros.append({"arquivo": pdf.name, "erro": str(e)})

    df_all = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

    # Alertas úteis para equipe (ajuste como quiser)
    alertas = pd.DataFrame()
    if not df_all.empty:
        alertas = df_all[df_all["Tipo"].isin(["INDEFINIDO"])].copy()

    resumo = {
        "pasta_entrada": str(pasta),
        "total_pdfs": len(pdfs),
        "pdfs_ok": len(dfs),
        "pdfs_erro": len(erros),
        "linhas_total": int(len(df_all)) if not df_all.empty else 0,
        "linhas_indefinidas": int(len(alertas)) if not alertas.empty else 0,
    }

    salvar_resultados(out_dir, erros, alertas, resumo)
    logger.info(f"Concluído. Saída em: {out_dir}")
    return out_dir

def main():
    root = tk.Tk()
    root.withdraw()

    messagebox.showinfo("Extrator - Ficha Gráfica", "Selecione a pasta contendo os PDFs.")
    pasta = filedialog.askdirectory(title="Selecione a pasta com PDFs")
    if not pasta:
        return

    messagebox.showinfo("Extrator - Ficha Gráfica", "Selecione a pasta de saída (onde salvar o Excel e logs).")
    out_root = filedialog.askdirectory(title="Selecione a pasta de saída")
    if not out_root:
        return

    try:
        out_dir = processar_pasta(Path(pasta), Path(out_root))
        messagebox.showinfo("Concluído", f"Processamento finalizado!\n\nSaída:\n{out_dir}")
    except Exception as e:
        messagebox.showerror("Erro", str(e))

    

if __name__ == "__main__":
    main()