"""
Utilitários de serialização JSON para DataFrames pandas.

O problema: pandas usa float('nan') para representar valores ausentes em
colunas numéricas/mistas. O json.dumps padrão do Python NÃO sabe serializar
NaN, lançando ValueError. FastAPI usa esse mesmo encoder internamente, então
qualquer resposta que contenha NaN resulta em 500.

Solução centralizada: substituir NaN por None (→ null em JSON) antes de
converter o DataFrame para lista de dicts.
"""

import math
from typing import Any

import pandas as pd


def safe_json_records(df: pd.DataFrame, n: int | None = None) -> list[dict[str, Any]]:
    """
    Converte um DataFrame em lista de dicts segura para JSON.

    - Aplica .head(n) se n for fornecido.
    - Substitui todos os valores NaN/NaT/inf por None antes de serializar,
      garantindo que o encoder JSON do FastAPI não lance ValueError.

    Args:
        df: DataFrame a ser convertido.
        n:  Número máximo de linhas a incluir (None = todas).

    Returns:
        Lista de dicts com valores NaN substituídos por None.
    """
    subset = df.head(n) if n is not None else df

    # Converte para records primeiro, depois sanitiza valor a valor.
    # Usar df.where() ou df.replace() pode falhar em DataFrames com tipos
    # mistos (object + float), então sanitizamos no nível Python pós-to_dict.
    raw_records = subset.to_dict(orient="records")
    return [_sanitize_row(row) for row in raw_records]


def _sanitize_row(row: dict[str, Any]) -> dict[str, Any]:
    """Substitui NaN, inf e -inf por None em um dict de uma linha."""
    return {k: _sanitize_value(v) for k, v in row.items()}


def _sanitize_value(value: Any) -> Any:
    """Retorna None se o valor for NaN ou ±inf, caso contrário retorna o valor original."""
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    # Trata também o tipo pandas NA/NaT via duck-typing
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        # pd.isna() pode lançar para tipos não escalares (listas, dicts etc.)
        pass
    return value
