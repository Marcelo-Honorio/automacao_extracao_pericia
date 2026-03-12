import pandas as pd
import re
import calendar

# função pra calcular dias
def dias(vetor):
    '''utilizar a coluna data'''
    # resultado = abs((vetor - vetor.shift(-1)).dt.days)
    resultado = abs((vetor - vetor.shift(-1)).dt.days)
    resultado.fillna(pd.Timedelta(0))
    return resultado

# funcao parar dias acumulados
def dias_acum(df):
    '''utilizar depois da função classificar e dias'''
    valor = 0
    resultado = []
    for i in df.index:
        if df["Historico"][i]=="juros_encarg_add": 
            valor = df['dias'][i]
            resultado.append(valor)
        else:
            valor = df['dias'][i] + valor
            resultado.append(valor)
    return resultado

# função base de calculo mês
def basecalculo_mes(vetor):
    resultado = vetor.apply(lambda x: calendar.monthrange(x.year, x.month)[1])
    return resultado

# função base de calculo ano
def basecalculo_ano(vetor):
    resultado = vetor.apply(lambda x: 366 if calendar.isleap(x.year) else 365)
    return resultado

# SN*D depois de calcular os dias
def SN_D(df):
    resultado = df.apply(lambda row: row["Saldo"]*row['dias'] if row["Saldo"] < 0 else 0, axis=1)
    resultado.fillna(0.00)
    return resultado

# Classificação do historico
def classificar(vetor):
    '''utilizar com o apply'''
    ## falta add correcao_enc
    categoria = {
        "amortizacao": r"(amortiza)",
        "capital": r"(capital|utiliza)",
        "tarifa": r"(estudo|opera|tarifa|contratacao)",
        "iof": r"(iof)",
        "juros_encarg_add":  r"^JUROS$",
        "juros_mora": r"(mora)",
        "multa": r"(multa|mult)",
        "seguro_penhor": r"(penh|penhor|seguro penhor)",
        "trans_saldo": r"(transf|tran|saldo)",
        "seguro_vida": r"(vida|seguro de vida)",
        "seguro_agricola": r"(agricola)"
        }
    for categoria, padrao in categoria.items():
        if re.search(padrao, vetor, re.IGNORECASE):
            return categoria

# SNA depois de calcular SN*D
def SNA(df):
    '''utilizar depois da função classificar e SN_D'''
    valor = 0
    resultado = []
    for i in df.index:
        if df["Historico"][i]=="juros_encarg_add": 
            valor = df['snd'][i]
            resultado.append(valor)
        else:
            valor = df['snd'][i] + valor
            resultado.append(valor)
    return resultado

## SNM depois de calcular SNA
def SNM(df, periodo):
    '''utilizar depois da função classificar e SNA'''
    valor = 0
    resultado = [0]
    for i in df[1:].index:
        match df["Historico"][i]:
            case "juros_encarg_add":
                valor = abs(df['sna'][i-1]/df['dias_acum'][i-1])
            case "correcao_enc": #não está na lista de classificacao
                valor = abs(df["Saldo"][i-1]) 
            case "multa":
                valor = abs(df["Saldo"][i-1]) 
            case "juros_mora" if periodo=='mensal':
                valor = abs(df["Saldo"][i-1])
            case "juros_mora" if periodo=='Cobrança única':
                valor = 0 #cobranca_unica ## REVER ESSA CONDICAO
            case _:
                valor = 0
        resultado.append(valor)
    return resultado

## Calcular os juros
def juros(df):
    x = ["juros_encarg_add", "correcao_enc", "multa", "juros_mora"]
    resultado = df.apply(lambda row: row["Debito"] if (row["Historico"] in x) else 0, axis=1)
    return resultado

## Calcular a taxa anual
def tx_anual(df, tx_equivalente):
    trans_saldo = df[df["Historico"] == 'trans_saldo'].loc[:,"Credito"].head(1)
    dia_saldo = df[df["Historico"] == 'trans_saldo'].loc[:,"Data"].head(1)
    valor = 0
    resultado = [0]
    for i in df[1:].index:
        match df["Historico"][i]:
            case 'juros_encarg_add':
                valor = ((1+df['juros'][i]/df['snm'][i])**(df['basecalculo_ano'][i]/df['dias_acum'][i]))-1
            case 'multa':
                valor = df['juros'][i]/df['snm'][i]
            case 'juros_mora' if tx_equivalente == "diaria": #coloca no input
                dias = (df['dias'][i] - dia_saldo).dt.days
                valor = trans_saldo/(dias*df['snm'][i])
            case 'juros_mora' if tx_equivalente == 'base30':
                valor = 0
                #mes #tirar duvida como é feito o mensal
            case _:
                valor = 0
        resultado.append(valor)
    return resultado

# Função para calcular a taxa juros mensal 
def tx_mensal(df, tx_equivalente):
    valor = 0
    resultado = [0]
    for i in df[1:].index:
        match df["Historico"][i]:
            case 'juros_encarg_add' if tx_equivalente == 'base30':
                if i != df.shape[0] - 1:
                    valor = ((1+df['juros'][i]/df['snm'][i])**(30/df['dias_acum'][i-1]))-1
                else:
                    valor = df['juros'][i]/df['snm'][i]
            case 'juros_encarg_add' if tx_equivalente == 'diaria':
                if i != df.shape[0] - 1:
                    valor = ((1+df['juros'][i]/df['snm'][i])**(df['basecalculo_ano'][i-1]/df['dias_acum'][i-1]))-1
                else:
                    valor = df['juros'][i]/df['snm'][i]
            case 'multa':
                valor = df['juros'][i]/df['snm'][i]
            case _:
                valor = 0
        resultado.append(valor)
    return resultado

# Estorno de credito seguindo os inputs da função no codigo ui.py
def estorno_credito(df, estornos):
    opcoes_estorno = [
            ("Seguro Penhor",  "seguro_penhor"),
            ("Seguro de Vida", "seguro_vida"),
            ("Seguro Agrícola","seguro_agricola"),
            ("Juros de Mora",         "juros_mora"),
            ("Tarifa",         "tarifa"),
        ]
    mapa_estorno = dict(opcoes_estorno)
    x = [mapa_estorno.get(i) for i in estornos]
    x.append("juros_encarg_add")

    resultado = df.apply(lambda row: row["Debito"] if (row["Historico"] in x) else 0, axis=1)
    return resultado

# Função para recalcular o saldo final, snd, sna, snm, juros_recal, juros_acumulado
def saldo_recalculado(df):
    # Trocar os NA po 0 nas colunas de crédito e debito
    df["Credito"] = df["Credito"].fillna(0)
    df["Debito"] = df["Debito"].fillna(0)

    p = df[df.Historico == "trans_saldo"].index[0]
    valor = 0
    x = 0
    a = 0
    saldo = []
    snd = []
    sna = []
    snm = []
    taxa_mercado = 0.1
    juros_recal = []
    juros_acumulado = []
    ## loop antes do transferencia de saldo
    for i in df[:p-1].index:
        #calculando o novo saldo
        valor = valor - df["Debito"][i] + df["Credito"][i] + df['estorno_credito'][i]
        saldo.append(valor)
        #novo SND
        if valor < 0:
            snd.append(valor*df["dias"][i])
        else:
            snd.append(0)
        #novo SNA
        if i > 0:
            if df["Historico"][i]=="juros_encarg_add":
                x=snd[i]
                sna.append(x)
            else:
                x=snd[i] + x
                sna.append(x)
        else:
            sna.append(0)
        #novo SNM 
        if df.Historico[i] == "juros_encarg_add":
            snm.append(sna[i-1]/df["dias_acum"][i-1])
        else:
            snm.append(0)
        #Função para o novo recalculo do juros 
        def recalculo_juros(indice):
            i=indice
            if df["tx_mensal"][i] <= taxa_mercado:
                x = (((1+df["tx_mensal"][i])**(df['dias_acum'][i-1]/30))-1)*snm[i]
                #juros_recal.append(x)
            else:
                x = (((1+taxa_mercado)**(df['dias_acum'][i-1]/30))-1)*snm[i]
                #juros_recal.append(x)
            return x
        #Novo calculo de juros recalculado
        if snm[i]<0:
            juros_recal.append(recalculo_juros(i))
        else:
            juros_recal.append(0)
        #Novo juros acumulado
        if i > 0:
            a = juros_acumulado[i-1] + juros_recal[i]
            juros_acumulado.append(a)
        else:
            juros_acumulado.append(0)
            
    
    #Calcular a ultima linha
    p = len(snm)
    snm.append(sna[p-1]/df["dias_acum"][p-1])
    #Calcular a ultima linha do juros recalculo
    if snm[p]<0:
        juros_recal.append(recalculo_juros(p))
    else:
        juros_recal.append(0)
    #Calcular a ultima linha do juros acumulado
    juros_acumulado.append(juros_acumulado[p-1]+juros_recal[p])

    valor = valor = valor - df["Debito"][i] + df["Credito"][i] + df['estorno_credito'][i] + juros_acumulado[p]
    saldo.append(valor)
    #adicionar o ultimo valor em sna e snd
    sna.append(0)
    snd.append(0)

    #Resultado 
    result = pd.DataFrame({
        "Saldo": saldo,
        "snd": snd,
        "sna": sna,
        "snm": snm,
        "juros_recal": juros_recal,
        "juros_acumulado": juros_acumulado,
    }, index=df.index[:p+1])

    return result

def finalizar_saldo(df,
                    col_saldo="Saldo",
                    marker_col="Historico",
                    marker_value="trans_saldo",
                    deb="Debito", cred="Credito", estc="estorno_credito"):
    # 1) localizar p (primeira linha com historico == "trans_saldo")
    mask = df[marker_col].eq(marker_value)
    if not mask.any():
        raise ValueError(f'Valor "{marker_value}" não encontrado em {marker_col}.')
    p_label = df.index[mask][0]                  # rótulo do índice
    p_pos   = df.index.get_loc(p_label)          # posição (segura mesmo com índice não numérico)

    # 2) garantir numérico e tratar NaN
    for c in (deb, cred, estc):
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    # 3) saldo inicial
    inicio = df.iloc[p_pos-1][col_saldo] if p_pos > 0 and pd.notna(df.iloc[p_pos-1][col_saldo]) else 0

    # 4) deltas e cumulativa a partir de p
    delta = -df[deb] + df[cred] + df[estc]
    df.loc[df.index[p_pos]:, col_saldo] = inicio + delta.iloc[p_pos:].cumsum()

    return df

# recalculo de juros
def juros_acumulado(df):

    mov = (
        df["Credito"]
        + df["estorno_credito"]
        - df["debito_recal"]
        - df["Debito"]
    )

    return mov.cumsum()

# Resultado de estorno
def estorno_resultado(df, estornos):
    opcoes_estorno = [
            ("Seguro Penhor",  "seguro_penhor"),
            ("Seguro de Vida", "seguro_vida"),
            ("Seguro Agrícola","seguro_agricola"),
            ("Juros de Mora",         "juros_mora"),
            ("Tarifa",         "tarifa"),
        ]
    mapa_estorno = dict(opcoes_estorno)
    x = [mapa_estorno.get(i) for i in estornos]
    
    resultado = df[df.Historico.isin(x)].groupby("Historico")["estorno_credito"].sum().to_dict()
    
    return resultado
