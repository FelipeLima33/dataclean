"""
Aplica as decisões do usuário (aprovar/editar/rejeitar) sobre os grupos
ambíguos de texto, depois de ele revisar na tela de Sugestões (Etapa 6).

Diferença importante em relação à Etapa 3/4:
- Etapa 3 só DETECTA os grupos ambíguos, não altera o dataset
- Etapa 4 só SUGERE o valor canônico via IA, não altera o dataset
- Este módulo é o que efetivamente troca os valores no DataFrame,
  e só faz isso para os grupos que o usuário aprovou (editados ou não)
"""

import pandas as pd


def apply_user_decisions(df: pd.DataFrame, decisions: list[dict]) -> tuple[pd.DataFrame, dict]:
    """
    decisions: lista de decisões do usuário, uma por grupo revisado:
        [
          {
            "column": "cidade",
            "variants": ["Belem", "belém", "BELEM"],
            "status": "approved",      # "approved" | "edited" | "rejected"
            "final_value": "Belém"     # obrigatório se approved/edited
          },
          ...
        ]

    Retorna:
        df_final: DataFrame com as substituições aplicadas
        report: quantas substituições foram feitas, por coluna
    """
    df_final = df.copy()
    report: dict = {}

    for decision in decisions:
        column = decision["column"]
        status = decision["status"]

        if status == "rejected":
            continue  # usuário decidiu manter os valores originais

        if column not in df_final.columns:
            continue  # coluna não existe mais (arquivo mudou entre etapas)

        variants = decision["variants"]
        final_value = decision["final_value"]

        mask = df_final[column].isin(variants)
        affected = int(mask.sum())

        if affected == 0:
            continue

        df_final.loc[mask, column] = final_value

        report.setdefault(column, {"replacements": 0, "groups_applied": 0})
        report[column]["replacements"] += affected
        report[column]["groups_applied"] += 1

    return df_final, report
