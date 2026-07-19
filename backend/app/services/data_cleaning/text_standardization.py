"""
Padronização de colunas de texto — reescrito na Etapa 10 depois de um
teste com dados reais revelar que o agrupamento por similaridade de
string (rapidfuzz) não pega abreviações nem sinônimos completamente
diferentes na escrita (ex: "SP" nunca vai ter alta similaridade textual
com "São Paulo", mesmo sendo a mesma cidade).

Nova abordagem: em vez de PRÉ-FILTRAR o que parece duplicata antes de
mandar pra IA (que é frágil pra abreviações), mandamos TODOS os valores
únicos de colunas com cara de categórica pra IA, e deixamos ELA decidir
os agrupamentos — a IA tem conhecimento de mundo suficiente pra saber
que "SP", "S. Paulo" e "São Paulo" são a mesma coisa, o que uma
comparação de string nunca vai captar.

Continua com duas fases:

1) LIMPEZA DETERMINÍSTICA (aqui, sem IA): espaços duplicados, espaços
   nas pontas.

2) SELEÇÃO DE CANDIDATOS PRA REVISÃO DA IA (aqui, sem decidir nada):
   identifica colunas categóricas (não texto livre, cardinalidade
   moderada) e reúne TODOS os valores únicos delas — a decisão de quais
   são a mesma coisa fica com a IA (Etapa 4).
"""

import pandas as pd

# Cardinalidade máxima (nº de valores únicos) pra considerar uma coluna
# "categórica" o suficiente pra valer a pena mandar pra revisão da IA.
# Acima disso, o custo/ruído de mandar tudo pra IA não compensa.
MAX_UNIQUE_VALUES_FOR_REVIEW = 60

# Proporção máxima de valores únicos em relação ao total de linhas —
# se quase toda linha tem um valor diferente, não é categórica, é
# provavelmente um identificador ou texto livre.
MAX_UNIQUE_RATIO_FOR_REVIEW = 0.3


def clean_whitespace(df: pd.DataFrame, text_columns: list[str] | None = None) -> pd.DataFrame:
    """Remove espaços duplicados e nas pontas de colunas de texto."""
    df_limpo = df.copy()

    if text_columns is None:
        text_columns = df_limpo.select_dtypes(include=["object"]).columns.tolist()

    for col in text_columns:
        df_limpo[col] = (
            df_limpo[col]
            .astype(str)
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )

    return df_limpo


def find_ambiguous_groups(
    df: pd.DataFrame,
    text_columns: list[str] | None = None,
) -> dict:
    """
    Identifica colunas categóricas candidatas à revisão da IA e reúne
    TODOS os seus valores únicos — sem tentar decidir aqui quais são
    duplicatas. Quem decide isso é a IA, na Etapa 4, com conhecimento
    de mundo que uma comparação de string não tem.

    Retorna, no mesmo formato usado pelas etapas seguintes (pra não
    quebrar nada rio abaixo):
        {
          "cidade": [
            {
              "variants": ["SP", "São Paulo", "sao paulo", "S. Paulo", ...],
              "occurrences": {"SP": 12, "São Paulo": 8, ...}
            }
          ],
          ...
        }
    Uma coluna só entra aqui se tiver MAIS DE 1 valor único — não faz
    sentido mandar pra revisão uma coluna sem nenhuma variação.
    """
    if text_columns is None:
        text_columns = df.select_dtypes(include=["object"]).columns.tolist()

    report: dict = {}

    for col in text_columns:
        values = df[col].dropna().astype(str)
        if values.empty:
            continue

        counts = values.value_counts()
        n_unique = len(counts)
        unique_ratio = n_unique / len(values)

        # Filtra fora: cardinalidade alta demais (não é categórica) ou
        # coluna sem nenhuma variação (nada pra revisar)
        if n_unique <= 1:
            continue
        if n_unique > MAX_UNIQUE_VALUES_FOR_REVIEW:
            continue
        if unique_ratio > MAX_UNIQUE_RATIO_FOR_REVIEW:
            continue

        report[col] = [
            {
                "variants": counts.index.tolist(),
                "occurrences": {k: int(v) for k, v in counts.items()},
            }
        ]

    return report
