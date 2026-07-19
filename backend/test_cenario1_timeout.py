"""
Teste de Cenário 1 — Chave do Groq inválida.
Mede o tempo total até resposta com o novo timeout de 10s por provedor.
"""

import os
import sys
import time

# ── Carrega .env ──────────────────────────────────────────────────────────────
for line in open(".env"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ[k.strip()] = v.strip().strip('"')

# ── Força chave inválida no Groq para simular o Cenário 1 ────────────────────
os.environ["GROQ_API_KEY"] = "gsk_INVALID_KEY_CENARIO1_TEST"

# ── Reinicia o client singleton do Groq (que pode já ter sido inicializado) ──
import app.services.ai.groq_client as groq_mod
groq_mod._client = None  # força reinicialização com a chave inválida

print("=" * 60)
print("CENÁRIO 1 — Groq com chave inválida")
print(f"Timeout por provedor: {10}s")
print("=" * 60)
print()

from app.services.ai.fallback import call_ai_with_fallback, PROVIDER_TIMEOUT_SECONDS

PROMPT = (
    "Retorne APENAS este JSON, sem texto adicional: "
    '{\"ok\": true, \"provider\": \"teste\"}'
)

print(f"Iniciando chamada… (timeout={PROVIDER_TIMEOUT_SECONDS}s por provedor)")
t_total_start = time.time()

try:
    response, provider = call_ai_with_fallback(PROMPT)
    elapsed = time.time() - t_total_start
    print()
    print(f"[OK] Resposta obtida via: {provider}")
    print(f"[OK] Tempo total: {elapsed:.2f}s")
    print()
    print("Resposta (primeiros 200 chars):")
    print(response[:200])
except Exception as e:
    elapsed = time.time() - t_total_start
    print()
    print(f"[FALHOU] Todos os provedores falharam apos {elapsed:.2f}s")
    print(f"Erro: {e}")
    sys.exit(1)

