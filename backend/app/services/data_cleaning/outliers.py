"""
Detecção de outliers em colunas numéricas.

Decisão de design: outliers NÃO são removidos automaticamente aqui.
Um valor fora da curva pode ser erro de digitação ou pode ser uma venda
real muito grande — decidir isso sem contexto é arriscado. Por isso o
outlier é apenas MARCADO no relatório (para aparecer na tela de
Diagnóstico), e a decisão de remover/manter fica com o usuário ou com
a etapa de revisão por IA.

Dois métodos disponíveis:
- IQR: mais robusto, não assume distribuição normal, melhor default
- z-score: mais sensível, mas assume dados aproximadamente normais

Usamos o skew (assimetria) da coluna para escolher automaticamente
o método mais adequado quando não especificado.
"""

import pandas as pd
import numpy as np


def _detect_iqr(series: pd.Series) -> pd.Series:
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return (series < lower) | (series > upper)


def _detect_zscore(series: pd.Series, threshold: float = 3.0) -> pd.Series:
    std = series.std()
    if std == 0 or pd.isna(std):
        return pd.Series(False, index=series.index)
    z = (series - series.mean()) / std
    return z.abs() > threshold


def detect_outliers(
    df: pd.DataFrame,
    numeric_columns: list[str] | None = None,
    method: str = "auto",
) -> dict:
    """
    Detecta outliers em cada coluna numérica.

    method: "iqr", "zscore" ou "auto" (escolhe IQR se a coluna for
    muito assimétrica — skew alto —, senão z-score)

    Retorna um dicionário por coluna:
        {
          "valor": {
             "method_used": "iqr",
             "outlier_count": 3,
             "outlier_indices": [12, 45, 201]
          },
          ...
        }
    """
    if numeric_columns is None:
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()

    report: dict = {}

    for col in numeric_columns:
        series = df[col].dropna()
        if len(series) < 4:
            continue  # dados de menos pra detectar outlier com sentido

        chosen_method = method
        if method == "auto":
            skew = series.skew()
            chosen_method = "iqr" if abs(skew) > 1 else "zscore"

        mask = (
            _detect_iqr(series)
            if chosen_method == "iqr"
            else _detect_zscore(series)
        )

        outlier_count = int(mask.sum())
        if outlier_count > 0:
            report[col] = {
                "method_used": chosen_method,
                "outlier_count": outlier_count,
                "outlier_indices": series[mask].index.tolist(),
            }

    return report
