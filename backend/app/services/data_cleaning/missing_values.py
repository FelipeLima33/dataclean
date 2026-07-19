"""
Tratamento de valores ausentes (imputação automática) — atualizado na
Etapa 10 depois de testes com dados reais revelarem dois bugs:

1. Colunas DERIVADAS (ex: valor_total = quantidade * valor_unitario)
   estavam sendo preenchidas com a mediana geral, o que produz números
   sem relação nenhuma com a linha real. Agora são recalculadas a
   partir das colunas que as compõem, quando possível.

2. Colunas de TEXTO LIVRE (opinião de cliente, comentário) estavam
   sendo preenchidas com a MODA (valor mais frequente) — o que faz
   parecer que dezenas de clientes escreveram a mesma frase, quando na
   verdade é só a imputação estatística inventando repetição. Texto
   livre agora recebe um placeholder neutro, nunca a moda.

Regra pros demais casos, sem mudança:
- Numérica "normal" (não derivada): mediana
- Texto categórico (poucos valores únicos se repetindo, ex: cidade,
  categoria): moda
"""

import pandas as pd

# Pares (coluna_derivada, [colunas_que_a_compõem], operação). Só
# recalcula se as colunas dos dois lados existirem no dataset. Ajuste
# esta lista conforme os padrões de coluna dos seus clientes reais.
DERIVED_COLUMNS = [
    ("valor_total", ["quantidade", "valor_unitario"], "multiply"),
]

# Limiar pra considerar uma coluna de texto como "texto livre" (opinião,
# comentário) em vez de categórica (cidade, categoria de produto):
# média de caracteres alta E baixa taxa de repetição de valores.
FREE_TEXT_MIN_AVG_LENGTH = 40
FREE_TEXT_MAX_REPEAT_RATIO = 0.3  # se o valor mais comum aparece em
                                   # mais de 30% das linhas, não é
                                   # texto livre de verdade


def _is_free_text_column(series: pd.Series) -> bool:
    non_null = series.dropna().astype(str)
    if non_null.empty:
        return False

    avg_length = non_null.str.len().mean()
    most_common_ratio = non_null.value_counts(normalize=True).iloc[0]

    return avg_length >= FREE_TEXT_MIN_AVG_LENGTH and most_common_ratio <= FREE_TEXT_MAX_REPEAT_RATIO


def _recalculate_derived_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Recalcula colunas derivadas (ex: valor_total) a partir das colunas
    que as compõem, SEMPRE que as colunas-fonte estiverem preenchidas —
    independente de a coluna derivada já ter um valor ou não.

    Motivo: business_rules.py pode NaN-ificar um valor inválido numa
    coluna-fonte (ex: quantidade negativa vira NaN, depois é imputada).
    Nesse caso a coluna derivada existia mas estava errada — sem o
    recálculo incondicional ela ficaria com o valor desatualizado.
    """
    df_result = df.copy()
    report: dict = {}

    for derived_col, source_cols, operation in DERIVED_COLUMNS:
        if derived_col not in df_result.columns:
            continue
        if not all(col in df_result.columns for col in source_cols):
            continue

        # Recalcula em TODAS as linhas onde as colunas-fonte estão
        # preenchidas — não só onde a derivada está ausente.
        # Isso corrige linhas onde a fonte foi corrigida por
        # business_rules (ex: quantidade -1 → NaN → imputada) mas
        # a coluna derivada já tinha um valor desatualizado.
        can_recalculate = df_result[source_cols].notna().all(axis=1)

        if can_recalculate.sum() == 0:
            continue

        if operation == "multiply":
            # Converte para numérico antes de multiplicar — evita TypeError
            # quando o CSV tem tipos trocados (ex: quantidade e valor_unitario
            # armazenados como string em vez de int/float).
            # errors="coerce" transforma valores não-numéricos em NaN, e
            # atualizamos can_recalculate para excluir essas linhas.
            numeric_sources = df_result[source_cols].apply(
                pd.to_numeric, errors="coerce"
            )
            can_recalculate = can_recalculate & numeric_sources.notna().all(axis=1)
            if can_recalculate.sum() == 0:
                continue
            recalculated = numeric_sources.loc[can_recalculate].prod(axis=1)
            df_result.loc[can_recalculate, derived_col] = recalculated

        report[derived_col] = {
            "recalculated_count": int(can_recalculate.sum()),
            "formula": f"{' * '.join(source_cols)}",
        }

    return df_result, report


def handle_missing_values(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Preenche valores ausentes coluna por coluna.

    Ordem:
    1. Imputação estatística de todas as colunas (mediana, moda ou
       placeholder para texto livre) — incluindo as colunas-fonte de
       colunas derivadas (ex: quantidade).
    2. Recálculo das colunas derivadas (ex: valor_total = quantidade *
       valor_unitario) DEPOIS da imputação, usando os valores já
       preenchidos nas fontes.

    Isso garante que uma coluna-fonte que estava ausente (ex: quantidade
    negativa → NaN via business_rules, depois imputada pela mediana)
    seja considerada no recálculo da coluna derivada, sobrescrevendo
    qualquer valor genérico que a imputação estatística tenha colocado.

    Retorna:
        df_limpo: DataFrame sem valores ausentes
        report: o que foi feito em cada coluna, para o diagnóstico
    """
    df_limpo = df.copy()
    report: dict = {}
    total_preenchido = 0

    for col in df_limpo.columns:
        n_missing = int(df_limpo[col].isna().sum())
        if n_missing == 0:
            continue

        if pd.api.types.is_numeric_dtype(df_limpo[col]):
            fill_value = df_limpo[col].median()
            strategy = "mediana"

        elif _is_free_text_column(df_limpo[col]):
            fill_value = "Sem comentário"
            strategy = "placeholder_texto_livre"

        else:
            mode = df_limpo[col].mode(dropna=True)
            fill_value = mode.iloc[0] if not mode.empty else "Desconhecido"
            strategy = "moda"

        df_limpo[col] = df_limpo[col].fillna(fill_value)

        report[col] = {
            "missing_count": n_missing,
            "strategy": strategy,
            "fill_value": fill_value,
        }
        total_preenchido += n_missing

    report["_summary"] = {"total_filled": total_preenchido}

    # Recalcula colunas derivadas DEPOIS da imputação — agora todas as
    # colunas-fonte já estão preenchidas, inclusive as que precisaram
    # de imputação estatística no loop acima.
    df_limpo, derived_report = _recalculate_derived_columns(df_limpo)
    report["_derived_columns"] = derived_report

    return df_limpo, report
