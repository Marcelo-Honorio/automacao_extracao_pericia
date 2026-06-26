import pandas as pd
import re
import calendar
from indices.bcb import obter_taxa_por_data

# função base de limpeza antes do cáculo
def moeda_para_float(valor):
    if pd.isna(valor):
        return 0.0

    if isinstance(valor, (int, float)):
        return float(valor)

    valor = str(valor).strip()

    valor = valor.replace("R$", "").replace(" ", "")
    valor = valor.replace(".", "").replace(",", ".")

    valor = re.sub(r"[^0-9\.-]", "", valor)

    if valor in ["", "-", ".", "-."]:
        return 0.0

    return float(valor)

# função pra calcular dias
def dias(vetor):
    """utilizar a coluna data"""
    # resultado = abs((vetor - vetor.shift(-1)).dt.days)
    resultado = vetor.shift(-1) - vetor
    # preencher o ultimo valor
    i = len(resultado)
    resultado[i - 1] = resultado[i - 2] - resultado[i - 2]
    return resultado


# funcao parar dias acumulados
def dias_acum(df):
    """utilizar depois da função classificar e dias"""
    valor = pd.Timedelta(0)
    resultado = []
    for i in df.index:
        if df.loc[i, "Historico"] == "juros_encarg_add":
            valor = df.loc[i, "dias"]
        else:
            valor = valor + df.loc[i, "dias"]

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
    """resultado = df.apply(lambda row: row["Saldo"]*row['dias'] if row["Saldo"] < 0 else 0, axis=1)
    resultado.fillna(0.00)
    return resultado"""
    dias = df["dias"] / pd.Timedelta(days=1)
    df["Saldo"] = df["Saldo"].apply(moeda_para_float)
    resultado = df["Saldo"].where(df["Saldo"] < 0, 0) * dias
    return resultado


# Classificação do historico
def classificar(vetor):
    """utilizar com o apply"""
    ## falta add correcao_enc
    categoria = {
        "amortizacao": r"(amortiza)",
        "capital": r"(capital|utiliza)",
        "tarifa": r"(estudo|opera|tarifa|contratacao)",
        "iof": r"(iof)",
        "juros_encarg_add": r"^JUROS$",
        "juros_mora": r"(mora)",
        "multa": r"(multa|mult)",
        "seguro_penhor": r"(penh|penhor|seguro penhor)",
        "trans_saldo": r"(transf|tran|saldo)",
        "seguro_vida": r"(vida|seguro de vida)",
        "seguro_agricola": r"(agricola)",
    }
    for categoria, padrao in categoria.items():
        if re.search(padrao, vetor, re.IGNORECASE):
            return categoria


# SNA depois de calcular SN*D
def SNA(df):
    """utilizar depois da função classificar e SN_D"""
    valor = 0
    resultado = []
    for i in df.index:
        if df["Historico"][i] == "juros_encarg_add":
            valor = df["snd"][i]
            resultado.append(valor)
        else:
            valor = df["snd"][i] + valor
            resultado.append(valor)
    return resultado


## SNM depois de calcular SNA
def SNM(df, periodo):
    """utilizar depois da função classificar e SNA"""
    valor = 0
    resultado = [0]
    for i in df[1:].index:
        match df["Historico"][i]:
            case "juros_encarg_add":
                dias = df.loc[i - 1, "dias_acum"] / pd.Timedelta(days=1)
                valor = abs(df.loc[i - 1, "sna"] / dias)
            case "correcao_enc":  # não está na lista de classificacao
                valor = abs(df.loc[i - 1, "Saldo"])
            case "multa":
                valor = abs(df.loc[i - 1, "Saldo"])
            case "juros_mora" if periodo == "mensal":
                valor = abs(df.loc[i - 1, "Saldo"])
            case "juros_mora" if periodo == "Cobrança única":
                valor = 0  # cobranca_unica ## REVER ESSA CONDICAO
            case _:
                valor = 0
        resultado.append(valor)
    return resultado


## Calcular os juros
def juros(df):
    x = ["juros_encarg_add", "correcao_enc", "multa", "juros_mora"]
    resultado = df.apply(
        lambda row: row["Debito"] if (row["Historico"] in x) else 0, axis=1
    )
    return resultado


## Calcular a taxa anual
def tx_anual(df, tx_equivalente):
    trans_saldo = df.loc[df["Historico"] == "trans_saldo", "Credito"].iloc[0]
    dia_saldo = df.loc[df["Historico"] == "trans_saldo", "Data"].iloc[0]

    resultado = [0]
    for i in df[1:].index:
        valor = 0
        match df.loc[i, "Historico"]:
            case "juros_encarg_add":
                if df.loc[i, "snm"] != 0 and df.loc[i, "dias_acum"] != 0:
                    dias_acum = df.loc[i - 1, "dias_acum"] / pd.Timedelta(days=1)
                    valor = (
                        (1 + df.loc[i, "juros"] / df.loc[i, "snm"])
                        ** (df.loc[i, "basecalculo_ano"] / dias_acum)
                    ) - 1
            case "multa":
                if df.loc[i, "snm"] != 0:
                    valor = df.loc[i, "juros"] / df.loc[i, "snm"]
            case "juros_mora":
                dias = (df.loc[i, "Data"] - dia_saldo).days
                if tx_equivalente == "diaria":
                    taxa_dia = df.loc[i, "juros"] / (trans_saldo * dias)
                    valor = (1 + taxa_dia) ** 365 - 1

                elif tx_equivalente == "base30":
                    taxa_mes = df.loc[i, "juros"] / (
                        trans_saldo * (dias / df.loc[i, "basecalculo_mes"])
                    )
                    valor = (1 + taxa_mes) ** 12 - 1  # coloca no input
            case _:
                valor = 0
        resultado.append(valor)
    return resultado


# Função para calcular a taxa juros mensal
def tx_mensal(df, tx_equivalente, periodo):
    valor = 0
    resultado = [0]
    for i in df[1:].index:
        match df["Historico"][i]:
            case "juros_encarg_add" if tx_equivalente == "base30":
                if i != df.shape[0] - 1:
                    dias_acum = df.loc[i - 1, "dias_acum"] / pd.Timedelta(days=1)
                    valor = (
                        (1 + df["juros"][i] / df["snm"][i]) ** (30 / dias_acum)
                    ) - 1
                else:
                    valor = df["juros"][i] / df["snm"][i]
            case "juros_encarg_add" if tx_equivalente == "diaria":
                if i != df.shape[0] - 1:
                    dias_acum = df.loc[i - 1, "dias_acum"] / pd.Timedelta(days=1)
                    valor = (
                        (1 + df["juros"][i] / df["snm"][i])
                        ** (df["basecalculo_mes"][i - 1] / dias_acum)
                    ) - 1
                else:
                    valor = df["juros"][i] / df["snm"][i]
            case "multa":
                valor = df["juros"][i] / df["snm"][i]
            case "juros_mora":
                if periodo == "mensal":
                    saldo = abs(df.loc[i - 1, "Saldo"])
                    valor_mora = df.loc[i, "Debito"]
                    dias_mes = df.loc[i - 1, "basecalculo_mes"]
                    dias_acum = int(df.loc[i - 1, "dias_acum"].days)
                    valor = (1 + (valor_mora/saldo))**((dias_mes/dias_acum) - 1)
                else:
                    ## Parametros para calculo de juros mora
                    data_trans = df[df.Historico == "trans_saldo"]["Data"].iloc[1]
                    valor_trans = df[df.Historico == "trans_saldo"]["Debito"].iloc[1]
                    data_mora = df.loc[i, "Data"]
                    valor_mora = df.loc[i, "Debito"]
                    dif = (data_mora - data_trans).days
                    ## calculo
                    valor = valor_mora / (dif * valor_trans) * 30
            case _:
                valor = 0
        resultado.append(valor)
    return resultado


# Estorno de credito seguindo os inputs da função no codigo ui.py
def estorno_credito(df, estornos, decisao):
    #opcoes_estorno = [
    #    ("Seguro Penhor", "seguro_penhor"),
    #    ("Seguro de Vida", "seguro_vida"),
    #    ("Seguro Agrícola", "seguro_agricola"),
    #    ("Juros de Mora", "juros_mora"),
    #    ("Tarifa", "tarifa"),
    #]
    #mapa_estorno = dict(opcoes_estorno)
    #x = [mapa_estorno.get(i) for i in estornos]
    estornos = set(estornos)

    if not decisao.capitalizacao_valida:
        estornos.update({"multa", "juros_mora", "juros_encarg_add"})

    x = list(estornos)
    resultado = df.apply(
        lambda row: row["Debito"] if (row["Historico"] in x) else 0, axis=1
    )
    return resultado

# Função para Historico de Estorno 
def historico_estorno(df, decisao):
    """
    Cria a coluna 'historico_estorno' apenas para linhas com estorno_credito > 0.
    Até 'trans_saldo' = adimplemento.
    Depois de 'trans_saldo' = inadimplemento.
    """

    HISTORICOS_MORA = {
        "juros_encarg_add",
        "juros_mora",
        "multa",
    }

    """
    No futuro preciso aprimorar a logica para os fundamentos e observações criados pela 
    função  decidir_capitalizacao()
    """

    #fund = "Não foi identificada cláusula expressa de capitalização de juros." 
    #ob_laudo = "Os encargos devem ser tratados sem capitalização contratualmente pactuada."

    #estorno_ad = None
    #estorno_inad = None

    if getattr(decisao, "observacoes_laudo", []) and len(decisao.observacoes_laudo) > 0:
        estorno_ad = "JUROS RECALCULADOS SEM CAPITALIZAÇÃO"

    if getattr(decisao, "fundamentos", []) and len(decisao.fundamentos) > 0:
        estorno_inad = "DESCARACTERIZAÇÃO DA MORA"

    df = df.copy()

    df["historico_norm"] = (
        df["Historico"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df["periodo_estorno"] = "inadimplemento"

    if df["historico_norm"].eq("trans_saldo").any():
        idx_trans_saldo = df.index[df["historico_norm"].eq("trans_saldo")][0]
        df.loc[:idx_trans_saldo, "periodo_estorno"] = "adimplemento"

    def montar_historico(row):
        historico_original = str(row.get("Historico", "")).strip()
        historico_norm = str(row.get("historico_norm", "")).strip()

        try:
            estorno = float(row.get("estorno_credito", 0) or 0)
        except (TypeError, ValueError):
            estorno = 0

        if estorno <= 0:
            return None

        if row["periodo_estorno"] == "adimplemento":
            if historico_norm in HISTORICOS_MORA and estorno_ad:
                return f"Estorno '{historico_original}'/{estorno_ad}"
            return f"Estorno '{historico_original}'"

        if row["periodo_estorno"] == "inadimplemento":
            if historico_norm in HISTORICOS_MORA and estorno_inad:
                return f"Estorno '{historico_original}'/{estorno_inad}"
            return f"Estorno '{historico_original}'"

        return None

    df["historico_estorno"] = df.apply(montar_historico, axis=1)

    df = df.drop(columns=["historico_norm"])

    return df

# incluir "JUROS RECALC. S/ CAP. E CAP. AO FIM DO PERÍODO DE NORMALIDADE"
def incluir_historico_final_normalidade(df):
    """
    No futuro essa função terá que levar em consideração os dados da decisao
    """
    df = df.copy()

    texto_final = "JUROS RECALC. S/ CAP. E CAP. AO FIM DO PERÍODO DE NORMALIDADE"

    mask = (
        df["periodo_estorno"].eq("adimplemento")
        & df["estorno_credito"].fillna(0).astype(float).gt(0)
    )

    if not mask.any():
        return df

    idx_ultimo_ad = df.index[mask][-1]

    historico = str(df.loc[idx_ultimo_ad, "Historico"]).strip()

    df.loc[idx_ultimo_ad, "historico_estorno"] = (
        f"Estorno '{historico}'/{texto_final}"
    )

    return df

# Função para recalcular o saldo final, snd, sna, snm, juros_recal, juros_acumulado
def saldo_recalculado(df, tx_mercado_opcao=["Nenhuma"]):
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
    juros_recal = []
    juros_acumulado = []

    def obter_taxa_aplicada(i):
        if "Nenhuma" in tx_mercado_opcao:
            return df["tx_mensal"][i]

        #if "Taxa limite - 12%" in tx_mercado_opcao:
        #    return (1 + 0.12) ** (1 / 12) - 1

        return df["tx_mercado"][i]

    for i in df[: p - 1].index:
        valor = valor - df["Debito"][i] + df["Credito"][i] + df["estorno_credito"][i]
        saldo.append(valor)

        if valor < 0:
            snd.append(valor * (df.loc[i, "dias"] / pd.Timedelta(days=1)))
        else:
            snd.append(0)

        if i > 0:
            if df["Historico"][i] == "juros_encarg_add":
                x = snd[i]
                sna.append(x)
            else:
                x = snd[i] + x
                sna.append(x)
        else:
            sna.append(0)

        if df.Historico[i] == "juros_encarg_add":
            dias_acum_ = df.loc[i - 1, "dias_acum"] / pd.Timedelta(days=1)
            snm.append(abs(sna[i - 1] / dias_acum_)) ## MUDANÇAS FEITAS
        else:
            snm.append(0)

        def recalculo_juros(indice):
            i = indice
            dias_acum_ = df.loc[i - 1, "dias_acum"] / pd.Timedelta(days=1)
            taxa_aplicada = obter_taxa_aplicada(i)

            return (((1 + taxa_aplicada) ** (dias_acum_ / 30)) - 1) * snm[i]

        if snm[i] > 0: # mudanças do sinal
            juros_recal.append(recalculo_juros(i))
        else:
            juros_recal.append(0)

        if i > 0:
            a = juros_acumulado[i - 1] + juros_recal[i]
            juros_acumulado.append(a)
        else:
            juros_acumulado.append(0)

    p = len(snm)
    dias_acum_ = df.loc[p - 1, "dias_acum"] / pd.Timedelta(days=1)
    snm.append(abs(sna[p - 1] / dias_acum_))

    if snm[p] > 0: # LINHA QUE MUDEI
        juros_recal.append(recalculo_juros(p))
    else:
        juros_recal.append(0)

    juros_acumulado.append(juros_acumulado[p - 1] + juros_recal[p])

    valor = (
        valor
        - df["Debito"][i]
        + df["Credito"][i]
        + df["estorno_credito"][i]
        + juros_acumulado[p]
    )

    saldo.append(valor)
    sna.append(0)
    snd.append(0)

    result = pd.DataFrame(
        {
            "Saldo": saldo,
            "snd": snd,
            "sna": sna,
            "snm": snm,
            "juros_recal": juros_recal,
            "juros_acumulado": juros_acumulado,
        },
        index=df.index[: p + 1],
    )

    return result


def finalizar_saldo(
    df,
    col_saldo="SALDO",
    marker_col="Historico",
    marker_value="trans_saldo",
    deb="Debito",
    cred="Credito",
    estc="estorno_credito",
):
    # 1) localizar p (primeira linha com historico == "trans_saldo")
    mask = df[marker_col].eq(marker_value)
    if not mask.any():
        raise ValueError(f'Valor "{marker_value}" não encontrado em {marker_col}.')
    p_label = df.index[mask][0]  # rótulo do índice
    p_pos = df.index.get_loc(p_label)  # posição (segura mesmo com índice não numérico)

    # 2) garantir numérico e tratar NaN
    for c in (deb, cred, estc):
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    # 3) saldo inicial
    inicio = (
        df.iloc[p_pos - 1][col_saldo]
        if p_pos > 0 and pd.notna(df.iloc[p_pos - 1][col_saldo])
        else 0
    )

    # 4) deltas e cumulativa a partir de p
    delta = -df[deb] + df[cred] + df[estc]
    df.loc[df.index[p_pos] :, col_saldo] = inicio + delta.iloc[p_pos:].cumsum()

    return df


# recalculo de juros
def juros_acumulado(df):

    mov = df["Credito"] + df["estorno_credito"] - df["debito_recal"] - df["Debito"]

    return mov.cumsum()


# Resultado de estorno
def estorno_resultado(df, estornos):
    #opcoes_estorno = [
    #    ("seguro_penhor", "Seguro Penhor"),
    #    ("seguro_vida", "Seguro de Vida"),
    #    ("seguro_agricola", "Seguro Agrícola"),
    #    ("juros_mora", "Juros de Mora"),
    #    ("tarifa", "Tarifa"),
    #]
    #mapa_estorno = dict(opcoes_estorno)
    #x = [mapa_estorno.get(i) for i in estornos]
    x = [item for item in estornos if item != "juros_encarg_add"]
    resultado = (
        df[df.Historico.isin(x)].groupby("Historico")["Debito"].sum().to_dict()
    )

    return resultado

# transformar taxa media de mercado anual em taxas mensal
def transf_anual_mensal(taxa):
    taxa = taxa / 100
    valor = (1 + taxa) ** (1 / 12) - 1
    return valor


# Função para calcular média entre as Taxas de Mercado
## Adicionar Taxa de Mercado
def taxa_mercado(df: pd.DataFrame, tx_mercado:dict, coluna_data: str = "Data") -> list:
    """
    Retorna uma lista com a taxa definida para cada data do DataFrame.

    tx_mercado esperado:
    {
        "codigo": "20769",
        "taxa": 0.0,
        "criterio": "C",
        "tmm": 13.83
    }
    """

    df = df.copy()

    if coluna_data not in df.columns:
        raise ValueError(f"Coluna de data '{coluna_data}' não encontrada no DataFrame.")

    if "snm" not in df.columns:
        raise ValueError("Coluna 'snm' não encontrada no DataFrame.")

    df[coluna_data] = pd.to_datetime(df[coluna_data], errors="coerce")

    if df[coluna_data].isna().any():
        raise ValueError(f"Existem datas inválidas na coluna '{coluna_data}'.")

    if not isinstance(tx_mercado, dict):
        raise TypeError("tx_mercado deve ser um dicionário com as chaves: codigo, taxa, criterio e tmm.")

    if "taxa" not in tx_mercado:
        raise ValueError("tx_mercado não possui a chave 'taxa'.")

    taxa = transf_anual_mensal(tx_mercado["taxa"])

    return [taxa if snm != 0 else None for snm in df["snm"]]

# Função para definir a taxa de mercado segundo as datas
def taxas_de_mercado(tx_selecionadas: list, dt_contrato: str):

    taxas_mercado = {}
    # codigos das tavas
    cod_taxa = {
        "20769": 20769,
        "20770": 20770,
    }

    for i in tx_selecionadas:
        cod = cod_taxa.get(i)
        if cod is not None:
            tx_data = obter_taxa_por_data(cod, dt_contrato)
            taxas_mercado[i] = tx_data["valor"]
    
    return taxas_mercado

# Função para decidir qual função para utilizar
def decidir_taxa(tx_opcoes, taxa_contrato, taxas_mercado=None):
    """
    tx_opcoes: lista vinda do input.
        Ex: ["20769"], ["20770"], ["Taxa limite - 12%"], ["Nenhum"]

    taxa_contrato: taxa do contrato em decimal.
        Ex: 0.18 para 18% a.a.

    taxa_mercado: taxa de mercado em decimal.
        Ex: 0.12 para 12% a.a.
    """
    taxas_mercado = taxas_mercado or {}

    C = taxa_contrato
    TL = 0.12

    resultados = []

    for codigo in tx_opcoes:

        if codigo in ("Nenhum", "Nenhuma"):
            resultados.append({
                "codigo": codigo,
                "taxa": C,
                "criterio": "C"
            })
            continue

        if codigo == "Taxa limite - 12%":
            resultados.append({
                "codigo": codigo,
                "taxa": min(C, TL),
                "criterio": "TL"
            })
            continue

        TMM = taxas_mercado.get(codigo)

        if TMM is None:
            continue

        TMM_15 = TMM * 1.5

        if TL > C > TMM_15:
            taxa = TMM
            criterio = "TMM"

        elif C > TL > TMM:
            taxa = TMM
            criterio = "TMM"

        elif C > TL and TL < TMM_15:
            taxa = TL
            criterio = "TL"

        elif C > TMM_15 > TL:
            taxa = TL
            criterio = "TL"

        elif C < TL < TMM:
            taxa = C
            criterio = "C"

        else:
            taxa = min(C, TL, TMM)
            criterio = "MENOR"

        resultados.append({
            "codigo": codigo,
            "taxa": taxa,
            "criterio": criterio,
            "tmm": TMM
        })

    return resultados
