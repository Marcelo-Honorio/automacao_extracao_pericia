
# Nomes corretos de estornos
OPCOES_ESTORNO = [
            ("Seguro Penhor",  "seguro_penhor"),
            ("Seguro de Vida", "seguro_vida"),
            ("Seguro Agrícola","seguro_agricola"),
            ("Juros de Mora", "juros_mora"),
            ("Tarifa",         "tarifa"),
        ]

# CHAVES E VALORES PARA OS ESTORNOS
ESTORNOS_MAP = {
    "seguro_penhor": {
        "chave": "seguro_penhor",
        "rotulo": "Seguro Penhor"
    },
    "seguro_vida": {
        "chave": "seguro_vida",
        "rotulo": "Seguro de Vida – Produtor Rural"
    },
    "seguro_agricola": {
        "chave": "seguro_agricola",
        "rotulo": "Seguro Agrícola"
    },
    "tarifa": {
        "chave": "tarifa",
        "rotulo": "Tarifa de Estudo de Operações"
    },
    "juros_mora": {
        "chave": "juros_mora",
        "rotulo": "Juros de Mora"
    }
}

# CHAVES E VALORES PARA OS ESTORNOS
INAD_MAP = {
    "remuneratorio_mora_a.m": {
        "chave": "remuneratorio_mora_a.m",
        "rotulo": "Juros remuneratórios + Juros de mora 1,00% a.m."
    },
    "remuneratorio_mora_a.a": {
        "chave": "remuneratorio_mora_a.a",
        "rotulo": "Juros remuneratórios + Juros de mora 1,00% a.a."
    },
    "multa_2_por": {
        "chave": "multa_2_por",
        "rotulo": "Multa contratual por inadimplemento: 2,00%."
    },
    "comissao": {
        "chave": "comissao",
        "rotulo": "Comissão de Permanência."
    }
}
