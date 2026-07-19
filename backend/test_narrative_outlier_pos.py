"""
Rodada extra: diagnostics com outliers > 0 para confirmar o fraseado positivo.
"""

import os, sys, json, time

for line in open(".env"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ[k.strip()] = v.strip().strip('"')

import app.services.ai.groq_client as groq_mod
import app.services.ai.openrouter_client as or_mod
import app.services.ai.nvidia_nim_client as nvidia_mod
groq_mod._client = or_mod._client = nvidia_mod._client = None

from app.services.ai.narrative import generate_narrative

SEP = "=" * 60

# Agora com outliers > 0
diagnostics = {
    "rows_before": 78,
    "duplicates_removed": 6,
    "missing_values_filled": 24,
    "outliers_adjusted": 5,   # campo legado com valor positivo
    "text_inconsistencies_resolved": 10,
}

charts_plan = [
    {"type": "boxplot", "column": "valor_unitario"},
    {"type": "boxplot", "column": "valor_total"},
    {"type": "mapa",    "column": "cidade"},
]

print()
print(SEP)
print("TESTE COM OUTLIERS > 0 — confirma fraseado correto (sem contradicao)")
print(SEP)
print()

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

text_lower = narrative_text.lower()

# Frases proibidas
bad_phrases = [
    "nao foram necessarios ajustes",
    "nao houve necessidade de ajuste",
    "nenhum ajuste foi necessario",
    "foram ajustados",
    "foram corrigidos automaticamente",
]
found_bad = [p for p in bad_phrases if p in text_lower]

# Frases esperadas com outliers > 0
good_phrases = ["sinali", "revisao", "identif", "detect"]
found_good = [p for p in good_phrases if p in text_lower]

print("VERIFICACOES:")
print(f"  [1] Frases proibidas ausentes?  {'OK' if not found_bad else 'FALHOU: ' + str(found_bad)}")
print(f"  [2] Fraseado correto presente?  {'OK (' + str(found_good) + ')' if found_good else 'AUSENTE — revisar'}")

all_ok = not found_bad
print()
print("RESULTADO:", "APROVADO" if all_ok else "REVISAR")
print()
print(SEP)
