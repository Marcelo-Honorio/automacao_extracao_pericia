from pathlib import Path
#from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import re

# função para restaurar o historico dos estornos que foram normalizados
def restaurar_historico_original(df):
    df = df.copy()

    def ajustar(row):
        texto = row.get("historico_estorno")

        if pd.isna(texto) or not texto:
            return texto

        historico_original = str(row.get("Historico", "")).strip()

        return re.sub(
            r"^Estorno\s+'[^']+'(.*)$",
            rf"Estorno '{historico_original}'\1",
            str(texto)
        )

    df["historico_estorno"] = df.apply(ajustar, axis=1)

    return df

def gerar_template_manual_xlsx(path_out: Path):
    """
    Gera um template simples para preenchimento manual.
    """
    import pandas as pd
    cols = ["Data", "Historico", "Debito", "Credito", "Saldo", "Saldo_geral"]
    df = pd.DataFrame(columns=cols)
    df.to_excel(path_out, index=False)


def processar_pasta(pasta: Path, out_root: Path, parent=None):
    # bibliotecas
    import pandas as pd
    import json
    import re
    from extrator.logging_utils import setup_logger
    #from extrator.io_utils import salvar_resultados
    from extrator.ficha_grafica import extrair_ficha_grafica_pdf  # sua função atual
    from extrator.fallback_xlsx import ler_ficha_grafica_manual_xlsx
    from extrator.validation import rodar_validacoes_e_decidir
    from pericia.process import process_df
    from pericia.oi_utils import salvar_resultados
    from laudo.render_xlsx import gerar_relatorio

    out_dir = out_root
    (out_dir / "logs").mkdir(parents=True, exist_ok=True)
    logger = setup_logger(out_dir / "logs")

    logger.info(f"Iniciando processamento da pasta: {pasta}")
    ## regex para capturar ficha gráfica
    padrao = re.compile(r'ficha\D*gr[aá]fica', re.IGNORECASE)
    pdfs = {p.stem: p for p in pasta.glob("*.pdf") if padrao.search(p.stem)}
    xlsx_in = {p.stem: p for p in pasta.glob("*.xlsx") if padrao.search(p.stem)}

    # pega XLSX já existentes na pasta de saída (corrigidos)
    # xlsx_out = {p.stem: p for p in out_dir.glob("*.xlsx")} -> SE PRECISAR INCLUIR NO FUTURO OS ARQUIVOS NA PASTA DE SAIDA
    
    # universo de itens por stem
    stems = sorted(set(pdfs.keys()) | set(xlsx_in.keys()))
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
            # xlsx_path = xlsx_out.get(stem) or xlsx_in.get(stem) -> SE PRECISAR INCLUIR NO FUTURO OS ARQUIVOS NA PASTA DE SAIDA
            xlsx_path = xlsx_in.get(stem)
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
            decisao = rodar_validacoes_e_decidir(df)
            with open(out_dir / "decisao.txt", 'w') as file:
                json.dump(decisao[1], file, indent=4)

            # bloqueia cálculo se necessário
            if not decisao[1]["pode_calcular"]:
                messagebox.showerror(
                    "Validação bloqueou o cálculo",
                    f"Não foi possível continuar.\n\n"
                    f"Motivo: {decisao[1]['motivo']}\n\n"
                    "Corrija o XLSX e rode novamente."
                )
                return

            # alerta mas permite continuar
            if decisao[1]["status"] == "ALERTA":
                messagebox.showwarning(
                    "Aviso de Validação",
                    f"Foram encontrados alertas:\n\n{decisao[1]['motivo']}\n\n"
                    "O cálculo continuará."
                )

            # =============================
            # AQUI entra o cálculo de pericia
            # =============================
            df_process, parametros, estorno_apurado  = process_df(df, stem, parent=parent, out_root=out_root)
            salvar_resultados(df_process, parametros, out_dir, stem) #Salvando os resultados da pericia (CORRIGIR ESSE PONTO)

            # salvar os parametros de todos os contratos
            parametros_contrato[stem] = parametros
            estornos_por_arquivo[stem] = estorno_apurado

            # =============================
            # AQUI os ANEXOS EXCEL
            # =============================
            df_process["Historico"] = df["Historico"].str.upper()
            df_process = restaurar_historico_original(df_process)
            gerar_relatorio(df_process, parametros, stem, out_dir)

            # consolida
            df2 = df_process.copy()
            df2["Stem"] = stem
            df2["Fonte"] = fonte
            df2["Status"] = decisao[1]["status"]
            dfs_consolidados.append(df2)

            status_rows.append({
                "stem": stem,
                "status": decisao[1]["status"],
                "fonte": fonte,
                "motivos": " | ".join(decisao[1]["motivo"]) if decisao[1]["motivo"] else ""
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

    from laudo.builder import transformar_input_para_contexto
    from laudo.render_docx import gerar_laudo_docx
    from laudo.estrutura_laudo import gerar_decisoes_irregularidade
    
    root = tk.Tk()
    root.withdraw()

    try:
        messagebox.showinfo("AutoPericia", "Selecione a pasta contendo os PDFs.", parent=root)
        pasta = filedialog.askdirectory(title="Selecione a pasta com PDFs", parent=root)
        if not pasta:
            return

        messagebox.showinfo("AutoPericia", "Selecione a pasta de saída (onde salvar o Excel e logs).", parent=root)
        out_root = filedialog.askdirectory(title="Selecione a pasta de saída", parent=root)
        if not out_root:
            return

        _, df, parametros_contrato, estornos_por_arquivo = processar_pasta(
            Path(pasta),
            Path(out_root),
            parent=root
            )

        contexto = transformar_input_para_contexto(parametros_contrato, estornos_por_arquivo)
        decisoes_irregularidades = gerar_decisoes_irregularidade(parametros_contrato)

        gerar_laudo_docx(Path(out_root), contexto, decisoes_irregularidades)

        messagebox.showinfo("Concluído", f"Processamento finalizado!\n\nSaída:\n{out_root}", parent=root)

    except Exception as e:
        messagebox.showerror("Erro", str(e), parent=root)

    finally:
        root.destroy()
    
if __name__ == "__main__":
    main()