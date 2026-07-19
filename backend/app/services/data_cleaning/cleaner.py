"""
Orquestrador da limpeza determinística (Etapa 3, atualizado na Etapa
10 com validação de regras de negócio depois de bugs encontrados em
teste com dados reais).

Ordem de execução (importa, mudou nesta etapa):
1. Limpeza de espaços em texto
2. Remoção de duplicatas
3. Validação de regras de negócio (quantidade/valor negativo vira
   ausente) — PRECISA vir antes da imputação, senão o valor inválido
   nunca é tratado
4. Valores ausentes — inclui os que acabaram de ser gerados no passo 3;
   recalcula colunas derivadas (ex: valor_total) antes de imputar
   estatisticamente qualquer coisa
5. Detecção de outliers (só marca, não remove)
6. Seleção de colunas categóricas candidatas à revisão de texto pela
   IA (reúne TODOS os valores únicos, não pré-filtra por similaridade)

O que sai daqui alimenta a tela de Diagnóstico e prepara os candidatos
que serão mandados em lote pra IA na Etapa 4.
"""

import pandas as pd

from .duplicates import remove_duplicates
from .missing_values import handle_missing_values
from .outliers import detect_outliers
from .text_standardization import clean_whitespace, find_ambiguous_groups
from .business_rules import validate_business_rules


def run_deterministic_cleaning(df: pd.DataFrame) -> dict:
    """
    Roda o pipeline completo de limpeza determinística.

    Retorna um dicionário com:
        - "cleaned_df": DataFrame já limpo
        - "diagnostics": números pra tela de Diagnóstico
        - "ambiguous_text_groups": candidatos de texto pra revisão da
          IA (Etapa 4) — NÃO foram alterados no df
        - "outliers": detalhe dos outliers encontrados (não removidos)
        - "business_rules_violations": o que foi corrigido por regra
          de negócio (ex: quantidades negativas)
    """
    rows_before = len(df)

    # 1. Espaços em texto
    df_step1 = clean_whitespace(df)

    # 2. Duplicatas
    df_step2, dup_report = remove_duplicates(df_step1)

    # 3. Regras de negócio — valores logicamente inválidos viram NaN
    df_step3, business_rules_report = validate_business_rules(df_step2)

    # 4. Valores ausentes (agora inclui os gerados no passo 3, e
    # recalcula colunas derivadas antes de imputar estatisticamente)
    df_step4, missing_report = handle_missing_values(df_step3)

    # 5. Outliers (detecção apenas — df não muda a partir daqui)
    outliers_report = detect_outliers(df_step4)

    # 6. Candidatos de texto pra revisão da IA (coluna inteira, sem
    # pré-filtro por similaridade — ver text_standardization.py)
    ambiguous_groups = find_ambiguous_groups(df_step4)

    text_inconsistencies_count = sum(
        len(groups) for groups in ambiguous_groups.values()
    )

    business_rules_violations_count = sum(
        v["invalid_count"] for v in business_rules_report.values()
    )

    diagnostics = {
        "rows_before": rows_before,
        "rows_after": len(df_step4),
        "duplicates_removed": dup_report["duplicates_removed"],
        "business_rules_violations_fixed": business_rules_violations_count,
        "missing_values_filled": missing_report["_summary"]["total_filled"],
        "outliers_flagged": sum(
            v["outlier_count"] for v in outliers_report.values()
        ),
        "text_inconsistencies_found": text_inconsistencies_count,
    }

    return {
        "cleaned_df": df_step4,
        "diagnostics": diagnostics,
        "missing_values_detail": missing_report,
        "outliers": outliers_report,
        "ambiguous_text_groups": ambiguous_groups,
        "business_rules_violations": business_rules_report,
    }
