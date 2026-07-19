"""
Cenario 2 definitivo: testa a rota /narrative com TODAS as IAs invalidas.

Abordagem:
1. Cria um dataset fake na memoria (memory_store)
2. Invalida todas as chaves de IA
3. Chama a funcao do handler da rota diretamente (async -> asyncio.run)
4. Verifica que a resposta contem o texto de fallback_local
5. Restaura as chaves

Nao precisa de servidor HTTP rodando — testa a logica da rota pura.
"""

import os
import sys
import asyncio
import json

# ── Carrega .env ──────────────────────────────────────────────────────────────
for line in open(".env"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ[k.strip()] = v.strip().strip('"')

SEP = "=" * 60

print()
print(SEP)
print("CENARIO 2 - Fallback local quando todas as IAs falham")
print(SEP)
print()

# ── Prepara dados falsos na memoria ──────────────────────────────────────────
import pandas as pd
from app.services.storage.memory_store import save_dataset

fake_df = pd.DataFrame({
    "produto": ["Notebook Dell", "Monitor LG"],
    "valor_total": [2697.0, 850.0],
    "cidade": ["Sao Paulo", "Rio de Janeiro"],
})

fake_diagnostics = {
    "rows_before": 78,
    "duplicates_removed": 6,
    "missing_values_filled": 24,
    "outliers_adjusted": 0,
    "text_inconsistencies_resolved": 10,
}

dataset_id = save_dataset(fake_df, fake_diagnostics, dataset_id="test-cenario2-fallback")
print(f"  Dataset fake salvo em memoria: {dataset_id}")

# ── Invalida as 3 chaves de IA ───────────────────────────────────────────────
import app.services.ai.groq_client as groq_mod
import app.services.ai.openrouter_client as or_mod
import app.services.ai.nvidia_nim_client as nvidia_mod

os.environ["GROQ_API_KEY"]       = "gsk_INVALIDA_CENARIO2"
os.environ["OPENROUTER_API_KEY"] = "sk-or-INVALIDA_CENARIO2"
os.environ["NVIDIA_API_KEY"]     = "nvapi-INVALIDA_CENARIO2"

groq_mod._client   = None
or_mod._client     = None
nvidia_mod._client = None

print("  Chaves de IA substituidas por valores invalidos.")
print()

# ── Chama o handler da rota diretamente ──────────────────────────────────────
from app.api.routes.narrative_route import get_narrative
import time

print(f"  Chamando get_narrative(dataset_id='{dataset_id}')...")
t0 = time.time()

result = asyncio.run(get_narrative(dataset_id))

elapsed = time.time() - t0
print(f"  Concluido em {elapsed:.2f}s")
print()

# ── Exibe resultado ──────────────────────────────────────────────────────────
print("  RESPOSTA COMPLETA:")
print("  " + "-" * 56)
print(json.dumps(result, indent=2, ensure_ascii=False))
print("  " + "-" * 56)
print()

# ── Verificacoes ─────────────────────────────────────────────────────────────
provider_used = result.get("provider_used", "")
narrative_text = result.get("narrative", "")

check1 = provider_used == "fallback_local"
check2 = "Sua planilha foi limpa com sucesso" in narrative_text
check3 = "narrativa detalhada" in narrative_text
check4 = "500" not in str(result)  # nao retornou erro 500

print("  VERIFICACOES:")
print(f"  [1] provider_used == 'fallback_local'?            {'OK' if check1 else 'FALHOU (got: ' + provider_used + ')'}")
print(f"  [2] Texto 'Sua planilha foi limpa...' presente?   {'OK' if check2 else 'FALHOU'}")
print(f"  [3] Menciona 'narrativa detalhada'?               {'OK' if check3 else 'FALHOU'}")
print(f"  [4] Nao retornou erro 500?                        {'OK' if check4 else 'FALHOU'}")
print()

all_pass = check1 and check2 and check3 and check4
print("  RESULTADO FINAL:", "PASSOU" if all_pass else "FALHOU")

# ── Restaura chaves ──────────────────────────────────────────────────────────
print()
print("  Restaurando chaves originais...")
for line in open(".env"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ[k.strip()] = v.strip().strip('"')

groq_mod._client   = None
or_mod._client     = None
nvidia_mod._client = None

print("  Chaves restauradas.")
print()
print(SEP)
print("CENARIO 2 CONCLUIDO")
print(SEP)

sys.exit(0 if all_pass else 1)
