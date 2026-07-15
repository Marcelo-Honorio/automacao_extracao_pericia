import pandas as pd
import pericia.ui as ui
import pericia.calculations as cal

from indices.bcb.service import atualizar_series_por_tx_mercado
from pericia.models import ParametrosContrato
from pericia.rules import decidir_capitalizacao
from pericia.oi_utils import salvar_parametros, obter_parametros_iniciais

def read_table_from_file(file_path):
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path, encoding="utf-8")
        else:
            df = pd.read_excel(file_path, engine="openpyxl")

        return df if not df.empty else None
    except Exception as e:
        print(f"Erro ao ler o arquivo {file_path}: {e}")


def process_df(df, stem, parent=None, out_root=None, pasta=None):
    #print(f"Processando arquivo:{}")
    print("ENTROU EM process_df")
    print("parent =", parent)
    parametros = {}
    estorno_apurado = {}

    if df is None or df.empty:
        raise ValueError(f"Nenhuma tabela encontrada para o arquivo: {stem}")

    colunas_necessarias = ["Data", "Historico", "Debito", "Credito", "Saldo"]
    faltantes = [c for c in colunas_necessarias if c not in df.columns]
    if faltantes:
        raise ValueError(
            f"O arquivo {stem} não possui as colunas necessárias: {faltantes}"
        )

    df = df[colunas_necessarias].copy()

    # renomear colunas    
    df.columns = ["Data", "Historico", "Debito", "Credito", "Saldo"]

    # converter a coluna data em datetime.date
    df.loc[:, "Data"] = pd.to_datetime(df["Data"], dayfirst=True).dt.date

    if df["Data"].isna().any():
        raise ValueError(f"Existem datas inválidas no arquivo: {stem}")

    # Caminho para parametros da pericia
    parametros_path = out_root / "parametros_inputs" / f"{stem}.json"

    # Solicitar entrada manual
    parametros_ini = obter_parametros_iniciais(
        parametros_path=parametros_path,
        pasta=pasta,
    )

    parametros_brutos = ui.create_input_with_options(
        stem,
        parametros_iniciais=parametros_ini,
        parent=parent,
        pasta=pasta,
    )

    salvar_parametros(parametros_path, parametros_brutos)

    parametros_obj = ParametrosContrato.from_dict(parametros_brutos)
    parametros_obj.validar()

    decisao_cap = decidir_capitalizacao(parametros_obj.capitalizacao)

    # Imprimir a decisão
    if not ui.confirmar_decisao_capitalizacao(decisao_cap, parent=parent):
        raise ValueError("Processamento interrompido pelo usuário após decisão de capitalização.")


    atualizar_series_por_tx_mercado(parametros_obj.tx_mercado) 

    taxas_mercado = cal.taxas_de_mercado(parametros_obj.tx_mercado, parametros_obj.data_contrato)
    taxas_parametros = cal.decidir_taxa(parametros_obj.tx_mercado, parametros_obj.juros_ano, taxas_mercado)
    tx_utilizada = min(taxas_parametros, key=lambda x: x['taxa'])
            
    # sequência do cálculo
    df.loc[:, "Historico"] = df["Historico"].apply(cal.classificar)
    df.loc[:, 'dias']=cal.dias(df["Data"])
    df.loc[:, 'dias_acum']=cal.dias_acum(df)
    df.loc[:, 'basecalculo_mes'] = cal.basecalculo_mes(df["Data"])
    df.loc[:, 'basecalculo_ano'] = cal.basecalculo_ano(df["Data"])
    df.loc[:, 'snd']=cal.SN_D(df)
    df.loc[:, 'sna']=cal.SNA(df)
    df.loc[:, 'snm']=cal.SNM(df, periodo=parametros_obj.periodo)
    df.loc[:, 'juros']=cal.juros(df)
    df.loc[:, "tx_mercado"] = cal.taxa_mercado(df, tx_mercado=tx_utilizada)
    df.loc[:, 'tx_anual'] = cal.tx_anual(df, tx_equivalente=parametros_obj.tx_equivalente)
    df.loc[:, 'tx_mensal'] = cal.tx_mensal(
                                            df, 
                                            tx_equivalente=parametros_obj.tx_equivalente,
                                            periodo=parametros_obj.periodo)

    # estornos escolhidos pelo usuário
    df.loc[:, 'estorno_credito'] = cal.estorno_credito(df, estornos=parametros_obj.estornos, decisao=decisao_cap)

    df = cal.historico_estorno(df, decisao_cap)
    df = cal.incluir_historico_final_normalidade(df)
    # regra adicional por decisão de capitalização
    # Aqui você escolhe a estratégia:
    # 1) simples: recalcula sem capitalização
    # 2) composto: mantém a lógica corrente
    # 3) afastar: gera coluna auxiliar / estorno adicional
    if decisao_cap.aplicar_regime == "simples":
        # ponto de expansão:
        # df = cal.aplicar_regime_simples(df)
        pass
    elif decisao_cap.aplicar_regime == "composto":
        # ponto de expansão:
        # df = cal.aplicar_regime_composto(df)
        pass
    elif decisao_cap.aplicar_regime == "afastar":
        # ponto de expansão:
        # df = cal.afastar_capitalizacao(df)
        pass

    # saldo recalculado
    df[["SALDO", "SND", "SNA", "SNM", "juros_recal", "juros_acumulado"]] = cal.saldo_recalculado(df, tx_mercado_opcao=parametros_obj.tx_mercado)

    # Juros recalculado
    df = cal.finalizar_saldo(df)

    # Calcular o debito recalculado e saldo recalculado
    df["debito_recal"] = 0.0
    posicao = df["juros_acumulado"].last_valid_index()
    if posicao is not None:
        df.loc[posicao, "debito_recal"] = df.loc[posicao, "juros_acumulado"]
    #df.loc[posicao, "debito_recal"] = df["juros_acumulado"].dropna().iloc[-1]
    
    # Coluna de juros recalculado
    df["saldo_recal"] = cal.juros_acumulado(df)

    parametros = parametros_obj.to_dict()
    #Decisao de capitalização
    parametros["decisao_capitalizacao"] = decisao_cap.to_dict()
    #Taxa utilizada
    parametros["taxa_utilizada"] = tx_utilizada

    ############################ EXCLUIR NO FUTURO #########################################
    #Resultado de pericia
    #if parametros["agente"].endswith(("réu","ré")):
    #    parametros["agente_continuidade"] = "da operação celebrada"
    #else:
    #    parametros["agente_continuidade"] = "das operações celebradas"

    # Separando substantivos nos parametros
    #parametros["substantivo"] = parametros["agente"].split()[1].capitalize()
    ###########################################################################################
    parametros.update(df[["Saldo", "saldo_recal"]].iloc[-1].to_dict())
    # Excesso de execução
    parametros["valor_excesso"] = abs(parametros["Saldo"] - parametros["saldo_recal"])

    # Data de execução/cobrança
    parametros["data_exec_cobra"] = cal.data_para_mes_ano(df.Data.iloc[-1])

    estorno_apurado = cal.estorno_resultado(df, estornos=parametros['estornos'])

    parametros["estorno_apurado"] = estorno_apurado
    parametros = parametros | cal.IOF_resultado(df)

    ## CORRIGINDO OS DIAS
    df.loc[:, "Data"] = [i.strftime("%d/%m/%Y") for i in df["Data"]]
    df.loc[:, "dias"] = [i.days for i in df.dias]
    #df.loc[:, "dias_acum"] = [i.days for i in df.dias_acum]
    df.loc[:, "dias_acum"] = df["dias_acum"].dt.days
    
    return df, parametros, estorno_apurado