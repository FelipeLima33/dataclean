"""
Validação de regras de negócio (Etapa 10).

Diferença importante em relação a outliers.py: um OUTLIER é um valor
estatisticamente incomum mas ainda possível (uma venda de R$15.000 pode
ser real). Uma violação de REGRA DE NEGÓCIO é um valor logicamente
impossível pro que a coluna representa (quantidade negativa não existe,
não importa a distribuição estatística).

Detectamos essas violações por PADRÃO DE NOME DE COLUNA (heurística
simples, sem dicionário fixo de nomes de coluna do cliente) e tratamos
como valor ausente — assim elas entram no mesmo fluxo de imputação
correta (incluindo o recálculo de colunas derivadas em missing_values.py)
em vez de passar batido pro arquivo final.
"""

import pandas as pd

# Palavras que sugerem "quantidade" — nunca pode ser negativa
QUANTITY_HINTS = ["quantidade", "qtd", "qty", "quantity", "unidades"]

# Palavras que sugerem "valor monetário" — negativo também é inválido
# na maioria dos contextos de venda (devoluções à parte, tratadas
# separadamente se o dataset tiver uma coluna própria pra isso)
MONETARY_HINTS = ["valor", "preco", "preço", "price", "total"]


def _column_matches(column_name: str, hints: list[str]) -> bool:
    normalized = column_name.lower()
    return any(hint in normalized for hint in hints)


def validate_business_rules(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Detecta valores logicamente inválidos (quantidade/valor negativo) e
    os transforma em NaN — para que sejam tratados corretamente pelo
    pipeline de valores ausentes, em vez de serem mantidos como estão.

    Retorna:
        df_validado: DataFrame com os valores inválidos zerados (NaN)
        report: quantas violações foram encontradas, por coluna
    """
    df_validado = df.copy()
    report: dict = {}

    numeric_columns = df_validado.select_dtypes(include="number").columns

    for col in numeric_columns:
        is_quantity = _column_matches(col, QUANTITY_HINTS)
        is_monetary = _column_matches(col, MONETARY_HINTS)

        if not (is_quantity or is_monetary):
            continue

        invalid_mask = df_validado[col] < 0
        invalid_count = int(invalid_mask.sum())

        if invalid_count > 0:
            df_validado.loc[invalid_mask, col] = pd.NA
            report[col] = {
                "rule": "quantidade_ou_valor_negativo",
                "invalid_count": invalid_count,
            }

    return df_validado, report
