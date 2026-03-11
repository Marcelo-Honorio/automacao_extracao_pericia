from pathlib import Path
#from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox

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
    #from extrator.io_utils import salvar_resultados
    from extrator.ficha_grafica import extrair_ficha_grafica_pdf  # sua função atual
    from extrator.fallback_xlsx import ler_ficha_grafica_manual_xlsx
    from extrator.validation import rodar_validacoes_e_decidir
    from pericia.process import process_df
    from pericia.oi_utils import salvar_resultados

    out_dir = out_root
    (out_dir / "logs").mkdir(parents=True, exist_ok=True)
    logger = setup_logger(out_dir / "logs")

    logger.info(f"Iniciando processamento da pasta: {pasta}")
    pdfs = {p.stem: p for p in pasta.glob("*.pdf")}
    xlsx_in = {p.stem: p for p in pasta.glob("*.xlsx")}

    # pega XLSX já existentes na pasta de saída (corrigidos)
    xlsx_out = {p.stem: p for p in out_dir.glob("*.xlsx")}

    # universo de itens por stem
    stems = sorted(set(pdfs.keys()) | set(xlsx_in.keys()) | set(xlsx_out.keys()))
    if not stems:
        raise RuntimeError("Nenhum PDF ou XLSX encontrado na pasta de entrada ou saída")

    status_rows = []
    dfs_consolidados = []
    erros = []
    parametros_contrato = {}
    estornos_por_arquivo = {}

    for stem in stems:
        try:
            # prioridade: XLSX da saída (corrigido) > XLSX da entrada (manual) > PDF 
            xlsx_path = xlsx_out.get(stem) or xlsx_in.get(stem)
            pdf_path = pdfs.get(stem)

            if xlsx_path:
                logger.info(f"[XLSX] {stem} -> {xlsx_path.name}")
                df = ler_ficha_grafica_manual_xlsx(xlsx_path, arquivo_origem=pdf_path.name if pdf_path else stem)
                fonte = "XLSX"
            elif pdf_path:
                logger.info(f"[PDF] {stem} -> {pdf_path.name}")
                df = extrair_ficha_grafica_pdf(str(pdf_path))
                fonte = "PDF"

                # salva o XLSX gerado pelo extrator na pasta de saída (mesmo stem)
                out_xlsx = out_dir / f"{stem}.xlsx"
                df.to_excel(out_xlsx, index=False)
                logger.info(f"Gerado: {out_xlsx.name}")
            else:
                # sem xlsx e sem pdf: não tem o que fazer
                status_rows.append({
                    "stem": stem,
                    "status": "FALHA",
                    "fonte": "NENHUMA",
                    "motivos": "Sem PDF e sem XLSX"
                })
                continue

            # rodas e salva relatório de validação
            df_alertas, decisao = rodar_validacoes_e_decidir(df)
            out_csv = out_dir / f"{stem}(VALIDACAO).csv"
            df_alertas.to_csv(out_csv, index=False, sep=";", encoding="utf-8-sig")

            # bloqueia cálculo se necessário
            if not decisao["pode_calcular"]:
                messagebox.showerror(
                    "Validação bloqueou o cálculo",
                    f"Não foi possível continuar.\n\n"
                    f"Motivo: {decisao['motivo']}\n\n"
                    "Corrija o XLSX e rode novamente."
                )
                return

            # alerta mas permite continuar
            if decisao["status"] == "ALERTA":
                messagebox.showwarning(
                    "Aviso de Validação",
                    f"Foram encontrados alertas:\n\n{decisao['motivo']}\n\n"
                    "O cálculo continuará."
                )

            # =============================
            # AQUI entra o cálculo de pericia
            # =============================
            df_process, parametros, estorno_apurado  = process_df(df, stem)
            salvar_resultados(df_process, parametros, out_dir, stem) #Salvando os resultados da pericia

            # salvar os parametros de todos os contratos
            parametros_contrato[stem] = parametros
            estornos_por_arquivo[stem] = estorno_apurado

            # consolida
            df2 = df_process.copy()
            df2["Stem"] = stem
            df2["Fonte"] = fonte
            df2["Status"] = decisao["status"]
            dfs_consolidados.append(df2)

            status_rows.append({
                "stem": stem,
                "status": decisao["status"],
                "fonte": fonte,
                "motivos": " | ".join(decisao["motivo"]) if decisao["motivo"] else ""
            })

            # se veio do PDF e está REVISAR, o XLSX já foi salvo e a equipe corrige nele
            # se veio do XLSX e está REVISAR, a equipe já sabe que precisa revisar o manual/corrigido
    
        except Exception as e:
            logger.exception(f"Erro em {stem}: {e}")
            erros.append({"stem": stem, "erro": str(e)})
            status_rows.append({"stem": stem, "status": "ERRO", "fonte": "", "motivos": str(e)})

    # salva status.csv
    df_status = pd.DataFrame(status_rows).sort_values(["status", "stem"])
    df_status.to_csv(out_dir / "status.csv", index=False, sep=";", encoding="utf-8-sig")

    # salva consolidado
    df_all = pd.concat(dfs_consolidados, ignore_index=True) if dfs_consolidados else pd.DataFrame()
    # df_all.to_excel(out_dir / "dfs_consolidado.xlsx", index=False)

    # salva erros.csv
    if erros:
        pd.DataFrame(erros).to_csv(out_dir / "logs" / "erros.csv", index=False, sep=";", encoding="utf-8-sig")

    logger.info("Concluído.")
    return out_dir, df_all, parametros_contrato, estornos_por_arquivo


def main():
    #import pericia.ui as ui
    #import pericia.calculations as cal
    #import pericia.process as process_df
    from laudo.builder import transformar_input_para_contexto
    from laudo.render_docx import gerar_laudo_docx
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
        out_dir, df_all, parametros_contrato, estornos_por_arquivo = processar_pasta(Path(pasta), Path(out_root))
        df_all.to_excel(out_dir / "dfs_consolidado.xlsx", index=False)

        # Preparar os input do LAUDO
        contexto = transformar_input_para_contexto(parametros_contrato, estornos_por_arquivo)
        # Gerar o Laudo
        template_path = "laudo/templates/laudo_modelo.docx"
        gerar_laudo_docx(template_path, out_dir, contexto)

        messagebox.showinfo("Concluído", f"Processamento finalizado!\n\nSaída:\n{out_dir}")
    except Exception as e:
        messagebox.showerror("Erro", str(e))
    
if __name__ == "__main__":
    main()