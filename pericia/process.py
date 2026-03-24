import pandas as pd
import pericia.ui as ui
import pericia.calculations as cal
from indices.bcb.service import atualizar_series_por_tx_mercado

def read_table_from_file(file_path):
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path, encoding="utf-8")
        else:
            df = pd.read_excel(file_path, engine="openpyxl")

        return df if not df.empty else None
    except Exception as e:
        print(f"Erro ao ler o arquivo {file_path}: {e}")


def process_df(df, stem):
    #print(f"Processando arquivo:{}")
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

    # Solicitar entrada manual
    print("input de dados")
    parametros = ui.create_input_with_options(stem)

    # Atualizar apenas as séries necessárias para a taxa escolhida
    tx_mercado = parametros.get("tx_mercado")
    atualizar_series_por_tx_mercado(tx_mercado)
            
    # sequência do cálculo
    df.loc[:, "Historico"] = df["Historico"].apply(cal.classificar)
    df.loc[:, 'dias']=cal.dias(df["Data"])
    df.loc[:, 'dias_acum']=cal.dias_acum(df)
    df.loc[:, 'basecalculo_mes'] = cal.basecalculo_mes(df["Data"])
    df.loc[:, 'basecalculo_ano'] = cal.basecalculo_ano(df["Data"])
    df.loc[:, 'snd']=cal.SN_D(df)
    df.loc[:, 'sna']=cal.SNA(df)
    df.loc[:, 'snm']=cal.SNM(df, periodo=parametros['periodo'])
    df.loc[:, 'juros']=cal.juros(df)
    df.loc[:, "tx_mercado"] = cal.taxa_mercado(df, tx_mercado=parametros["tx_mercado"])
    df.loc[:, 'tx_anual'] = cal.tx_anual(df, tx_equivalente=parametros['tx_equivalente'])
    df.loc[:, 'tx_mensal'] = cal.tx_mensal(df, tx_equivalente=parametros['tx_equivalente'])
    df.loc[:, 'estorno_credito'] = cal.estorno_credito(df, estornos=parametros['estornos'])

    # saldo recalculado
    df[["SALDO", "SND", "SNA", "SNM", "juros_recal", "juros_acumulado"]] = cal.saldo_recalculado(df)

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

    #Resultado de pericia
    if parametros["agente"].endswith(("réu","ré")):
        parametros["agente_continuidade"] = "da operação celebrada"
    else:
        parametros["agente_continuidade"] = "das operações celebradas"

    # Separando substantivos nos parametros
    parametros["substantivo"] = parametros["agente"].split()[1].capitalize()

    parametros.update(df[["SALDO", "saldo_recal"]].iloc[-1].to_dict())
    estorno_apurado = cal.estorno_resultado(df, estornos=parametros['estornos'])

    ## CORRIGINDO OS DIAS
    df.loc[:, "Data"] = [i.strftime("%d/%m/%Y") for i in df["Data"]]
    df.loc[:, "dias"] = [i.days for i in df.dias]
    df.loc[:, "dias_acum"] = [i.days for i in df.dias_acum]
    
    return df, parametros, estorno_apurado