"""
Testa a narrativa com o novo prompt corrigido para outliers.
Usa os mesmos diagnostics e charts_plan do dataset vendas_teste_dataclean.csv
(com boxplots em valor_unitario e valor_total) para verificar que a
contradicao foi eliminada.
"""

import os
import sys
import asyncio
import json

# Carrega .env
for line in open(".env"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ[k.strip()] = v.strip().strip('"')

# Reinicia singletons de IA (garantia de chave real)
import app.services.ai.groq_client as groq_mod
import app.services.ai.openrouter_client as or_mod
import app.services.ai.nvidia_nim_client as nvidia_mod
groq_mod._client = or_mod._client = nvidia_mod._client = None

from app.services.ai.narrative import generate_narrative

SEP = "=" * 60

# Diagnostics identicos ao que o servidor gerou durante o teste anterior
diagnostics = {
    "rows_before": 78,
    "duplicates_removed": 6,
    "missing_values_filled": 24,
    "outliers_adjusted": 0,          # nenhum outlier "ajustado" (campo legado)
    "text_inconsistencies_resolved": 10,
}

# Charts plan com 2 boxplots (igual ao dataset real)
charts_plan = [
    {"type": "boxplot", "column": "valor_unitario"},
    {"type": "boxplot", "column": "valor_total"},
    {"type": "mapa",    "column": "cidade"},
    {"type": "mapa",    "column": "estado"},
]

print()
print(SEP)
print("TESTE DO PROMPT CORRIGIDO — outliers sem contradicao")
print(SEP)
print()
print("Diagnostics:")
print(json.dumps(diagnostics, indent=2, ensure_ascii=False))
print()
print("Charts plan: 2 boxplots (valor_unitario, valor_total) + 2 mapas")
print()

import time
t0 = time.time()
narrative_text, provider = generate_narrative(diagnostics, charts_plan)
elapsed = time.time() - t0

print(f"Concluido em {elapsed:.2f}s via '{provider}'")
print()
print("NARRATIVA GERADA:")
print("-" * 56)
print(narrative_text)
print("-" * 56)
print()

# Verificacoes automaticas de contradicao
text_lower = narrative_text.lower()

bad_phrases = [
    "nao foram necessarios ajustes",
    "nao houve necessidade de ajuste",
    "nenhum ajuste foi necessario",
    "sem necessidade de ajuste",
    "nao precisou de ajuste",
]

contradictions_found = []
for bad in bad_phrases:
    if bad in text_lower:
        contradictions_found.append(bad)

print("VERIFICACOES:")
print(f"  [1] Menciona 'sinalizados para revisao'?        ", end="")
check1 = "sinalizados" in text_lower or "revisao" in text_lower or "revisao manual" in text_lower or "sinali" in text_lower
print("OK" if check1 else "AUSENTE (mas pode estar OK se outliers=0)")

print(f"  [2] Nao usa linguagem de 'ajuste' para outliers?  ", end="")
check2 = len(contradictions_found) == 0
print("OK" if check2 else "FALHOU — frases problematicas: " + str(contradictions_found))

print(f"  [3] Nao ha contradicao outlier detectado+ajustado? ", end="")
has_detected = "identific" in text_lower or "detect" in text_lower or "sinaliz" in text_lower
has_adjusted = "ajustamos" in text_lower or "foram ajustados" in text_lower or "foram corrigidos" in text_lower
check3 = not (has_detected and has_adjusted)
print("OK" if check3 else "FALHOU — descreve outliers como detectados E ajustados")

print()
all_ok = check2 and check3
print("RESULTADO:", "APROVADO" if all_ok else "REVISAR")
print()
print(SEP)
