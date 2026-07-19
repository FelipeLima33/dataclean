"""
Remoção de linhas duplicadas.

Regra determinística: uma linha é duplicata se TODAS as colunas forem
idênticas a outra linha já vista. Mantemos a primeira ocorrência.
"""

import pandas as pd


def remove_duplicates(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Remove linhas 100% duplicadas.

    Retorna:
        df_limpo: DataFrame sem duplicatas
        report: dicionário com o que foi feito, para o diagnóstico da tela 2
    """
    total_antes = len(df)

    duplicated_mask = df.duplicated(keep="first")
    df_limpo = df.loc[~duplicated_mask].reset_index(drop=True)

    total_removido = int(duplicated_mask.sum())

    report = {
        "duplicates_found": total_removido,
        "duplicates_removed": total_removido,
        "rows_before": total_antes,
        "rows_after": len(df_limpo),
    }

    return df_limpo, report
