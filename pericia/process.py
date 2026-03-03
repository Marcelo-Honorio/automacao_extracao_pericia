import pandas as pd
import os
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


def process_df(df):
    #print(f"Processando arquivo:{}")

    df = df[["Data", "Historico", "Debito", "Credito", "Saldo"]]
  
    if df is not None:
        #renomear colunas
        df.columns = ['data', 'historico', 'debito', 'credito', 'saldo']

        # converter a coluna data em datetime
        df['data'] = pd.to_datetime(df['data'], format='%d.%m.%Y')

        # selecionar as colunas
        df = df.loc[:, ['data', 'historico', 'debito', 'credito', 'saldo']]
        
        ## Salvar em CSV ou Excel, se necessário
       
        # Solicitar entrada manual
        print("input de dados")
        user_data = ui.create_input_with_options()
               
        ## sequencia deve ser seguida
        df['historico'] = df.historico.apply(cal.classificar)
        df['dias']=cal.dias(df['data'])
        df['dias_acum']=cal.dias_acum(df)
        df['basecalculo_mes'] = cal.basecalculo_mes(df['data'])
        df['basecalculo_ano'] = cal.basecalculo_ano(df['data'])
        df['snd']=cal.SN_D(df)
        df['sna']=cal.SNA(df)
        df['snm']=cal.SNM(df, periodo=user_data['periodo'])
        df['juros']=cal.juros(df)
        df['tx_anual'] = cal.tx_anual(df, tx_equivalente=user_data['tx_equivalente'])
        df['tx_mensal'] = cal.tx_mensal(df, tx_equivalente=user_data['tx_equivalente'])
        df['estorno_credito'] = cal.estorno_credito(df, estornos=user_data['estornos'])

        #saldo, snd, sna, snm, juros_recal, juros_acumulado = saldo_recalculado(df)
        df[["saldo", "snd", "sna", "snm", "juros_recal", "juros_acumulado"]] = cal.saldo_recalculado(df)

        df = cal.finalizar_saldo(df)

        caminho = os.getcwd()+'\\.gitignore\\resultado\\tabela_final.csv'
        df.to_csv(caminho, index=False)     
    else:
        print("Nenhuma tabela encontrada")
        