import pandas as pd
import json
import pericia.ui as ui
import pericia.calculations as cal

def read_table_from_file(file_path):
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path, encoding="utf-8")
        else:
            df = pd.read_excel(file_path, engine="openpyxl")

        return df if not df.empty else None
    except Exception as e:
        print(f"Erro ao ler o arquivo {file_path}: {e}")


def process_df(df, out_dir, stem):
    #print(f"Processando arquivo:{}")

    df = df[["Data", "Historico", "Debito", "Credito", "Saldo"]]
  
    if df is not None:
        #renomear colunas
        df.columns = ["Data", "Historico", "Debito", "Credito", "Saldo"]

        # converter a coluna data em datetime
        df["Data"] = pd.to_datetime(df["Data"], dayfirst=True)

        # selecionar as colunas
        df = df.loc[:, ["Data", "Historico", "Debito", "Credito", "Saldo"]]
        
        ## Salvar em CSV ou Excel, se necessário
       
        # Solicitar entrada manual
        print("input de dados")
        user_data = ui.create_input_with_options(stem)
               
        ## sequencia deve ser seguida
        df["Historico"] = df.Historico.apply(cal.classificar)
        df['dias']=cal.dias(df["Data"])
        df['dias_acum']=cal.dias_acum(df)
        df['basecalculo_mes'] = cal.basecalculo_mes(df["Data"])
        df['basecalculo_ano'] = cal.basecalculo_ano(df["Data"])
        df['snd']=cal.SN_D(df)
        df['sna']=cal.SNA(df)
        df['snm']=cal.SNM(df, periodo=user_data['periodo'])
        df['juros']=cal.juros(df)
        df['tx_anual'] = cal.tx_anual(df, tx_equivalente=user_data['tx_equivalente'])
        df['tx_mensal'] = cal.tx_mensal(df, tx_equivalente=user_data['tx_equivalente'])
        df['estorno_credito'] = cal.estorno_credito(df, estornos=user_data['estornos'])

        #saldo, snd, sna, snm, juros_recal, juros_acumulado = saldo_recalculado(df)
        df[["Saldo", "snd", "sna", "snm", "juros_recal", "juros_acumulado"]] = cal.saldo_recalculado(df)

        # Juros recalculado
        df = cal.finalizar_saldo(df)

        # Calcular o debito recalculado e saldo recalculado
        df["debito_recal"] = 0.0
        posicao = df.index[df["juros_acumulado"].last_valid_index()]
        df.loc[posicao, "bebito_recal"] = df["juros_acumulado"].dropna().iloc[-1]

        df["saldo_recal"] = cal.juros_acumulado(df)

        #Salvando os parametros
        with open(out_dir/ 'parametros.txt', 'w') as file:
            json.dump(user_data, file, indent=4)

        #Salvando a ficha processada
        df.to_excel(out_dir/ f"{stem}(PROCESSADO).xlsx", index=False)

        #Resultado de pericia
        resultados_pericia = df[["Saldo", "saldo_recal"]].iloc[-1].to_dict()
        resultados_pericia.update(cal.estorno_resultado(df, estornos=user_data['estornos']))
    else:
        print("Nenhuma tabela encontrada")

    return df, resultados_pericia

