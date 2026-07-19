"""
Teste do endpoint de narrativa automatica.

CENARIO 1: Fluxo completo (resolve-ambiguous -> apply-decisions -> narrative)
CENARIO 2: Fallback quando todas as 3 chaves de IA estao invalidas

Roda tudo via HTTP contra o servidor na porta 8002.
Para o Cenario 2, invalida as chaves no ambiente e reinicia os singletons
dos clientes de IA diretamente no modulo (sem precisar reiniciar o servidor).
"""

import os
import sys
import json
import time
import requests

BASE_URL = "http://127.0.0.1:8002/api"
CSV_PATH = r"tests\fixtures\vendas_teste_dataclean.csv"

SEP = "=" * 60


# ─────────────────────────────────────────────────────────────────────────────
# Utilitarios
# ─────────────────────────────────────────────────────────────────────────────

def check_server():
    try:
        r = requests.get("http://127.0.0.1:8002/", timeout=3)
        return r.status_code == 200
    except Exception:
        return False

def pprint_json(data: dict):
    print(json.dumps(data, indent=2, ensure_ascii=False))


# ─────────────────────────────────────────────────────────────────────────────
# CENARIO 1 — Caminho normal
# ─────────────────────────────────────────────────────────────────────────────

def run_cenario1():
    print(SEP)
    print("CENARIO 1 — Fluxo completo + narrativa (IA real)")
    print(SEP)

    # 1. resolve-ambiguous
    print("\n[1/3] POST /api/clean/resolve-ambiguous ...")
    t0 = time.time()
    with open(CSV_PATH, "rb") as f:
        res = requests.post(f"{BASE_URL}/clean/resolve-ambiguous", files={"file": f})
    elapsed = time.time() - t0

    if res.status_code != 200:
        print(f"  ERRO {res.status_code}: {res.text[:300]}")
        sys.exit(1)

    data = res.json()
    dataset_id = data["dataset_id"]
    ai_decisions_raw = data.get("ai_decisions", {})
    provider_step1 = data.get("provider_used", "?")
    print(f"  OK em {elapsed:.2f}s | dataset_id={dataset_id} | provedor={provider_step1}")
    print(f"  Sugestoes da IA: {sum(len(v) for v in ai_decisions_raw.values())} grupos em {len(ai_decisions_raw)} coluna(s)")

    # 2. build decisions (aprovando todas as sugestoes)
    decisions = []
    for col, items in ai_decisions_raw.items():
        for item in items:
            decisions.append({
                "column": col,
                "variants": item["variants"],
                "status": "approved",
                "final_value": item["canonical"],
            })
    print(f"  {len(decisions)} decision(s) montadas (todas aprovadas)")

    # 3. apply-decisions
    print("\n[2/3] POST /api/clean/apply-decisions ...")
    t0 = time.time()
    with open(CSV_PATH, "rb") as f:
        res2 = requests.post(
            f"{BASE_URL}/clean/apply-decisions",
            files={"file": f},
            data={"decisions": json.dumps(decisions), "dataset_id": dataset_id},
        )
    elapsed = time.time() - t0

    if res2.status_code != 200:
        print(f"  ERRO {res2.status_code}: {res2.text[:300]}")
        sys.exit(1)

    data2 = res2.json()
    print(f"  OK em {elapsed:.2f}s")

    # 4. narrative
    print(f"\n[3/3] GET /api/narrative/{dataset_id} ...")
    t0 = time.time()
    res3 = requests.get(f"{BASE_URL}/narrative/{dataset_id}", timeout=60)
    elapsed = time.time() - t0

    if res3.status_code != 200:
        print(f"  ERRO {res3.status_code}: {res3.text[:300]}")
        sys.exit(1)

    data3 = res3.json()
    print(f"  OK em {elapsed:.2f}s\n")
    print("  provider_used :", data3.get("provider_used"))
    print()
    print("  NARRATIVE:")
    print("  " + "-" * 56)
    narrative_text = data3.get("narrative", "")
    for line in narrative_text.split(". "):
        if line.strip():
            print(f"  {line.strip()}.")
    print("  " + "-" * 56)

    return dataset_id, data3


# ─────────────────────────────────────────────────────────────────────────────
# CENARIO 2 — Fallback quando todas as IAs falham
# ─────────────────────────────────────────────────────────────────────────────

def invalidate_ai_keys():
    """
    Troca as chaves de IA no ambiente do processo Python ATUAL e
    reinicia os singletons dos clientes SDK, simulando chaves invalidas.
    (O servidor ja esta rodando em outro processo; aqui nos testamos a
     rota /narrative diretamente para garantir que o fallback_local ativa.)
    """
    # Para o Cenario 2 vamos chamar a rota via HTTP, mas o servidor
    # usa as chaves que foram carregadas quando ele iniciou.
    # A unica forma de testar o fallback_local via HTTP e reiniciar o
    # servidor com chaves invalidas.
    # Aqui fazemos isso modificando o .env temporariamente.
    pass


def run_cenario2_inprocess(dataset_id: str):
    """
    Testa o fallback_local chamando generate_narrative() diretamente,
    com os singletons de IA apontando para chaves invalidas.
    Isso evita precisar reiniciar o servidor.
    """
    print()
    print(SEP)
    print("CENARIO 2 — Fallback quando todas as 3 IAs falham (in-process)")
    print(SEP)
    print()
    print("  Invalidando chaves de IA nos singletons de cliente...")

    # Carrega .env para ter as variaveis de ambiente disponiveis
    for line in open(".env"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip().strip('"')

    # Importa modulos e reseta singletons para forcar recriar com chave invalida
    import app.services.ai.groq_client as groq_mod
    import app.services.ai.openrouter_client as or_mod
    import app.services.ai.nvidia_nim_client as nvidia_mod

    os.environ["GROQ_API_KEY"]       = "gsk_INVALIDA_CENARIO2"
    os.environ["OPENROUTER_API_KEY"] = "sk-or-INVALIDA_CENARIO2"
    os.environ["NVIDIA_API_KEY"]     = "nvapi-INVALIDA_CENARIO2"

    groq_mod._client   = None
    or_mod._client     = None
    nvidia_mod._client = None

    print("  Chaves substituidas por valores invalidos.")
    print()

    # Simula os dados que o servidor teria na memoria apos o apply-decisions
    # (usamos os mesmos diagnostics que a rota real teria salvo)
    fake_diagnostics = {
        "rows_before": 100,
        "duplicates_removed": 3,
        "missing_values_filled": 7,
        "outliers_adjusted": 2,
        "text_inconsistencies_resolved": 4,
    }
    fake_charts_plan = [
        {"type": "boxplot", "column": "valor_unitario"},
    ]

    print("  Chamando generate_narrative() com todas as IAs invalidas...")
    t0 = time.time()
    try:
        from app.services.ai.narrative import generate_narrative
        narrative_text, provider = generate_narrative(fake_diagnostics, fake_charts_plan)
        elapsed = time.time() - t0
        print(f"  Concluido em {elapsed:.2f}s\n")
        print("  provider_used :", provider)
        print()
        print("  NARRATIVE:")
        print("  " + "-" * 56)
        print(f"  {narrative_text}")
        print("  " + "-" * 56)

        # Verificacoes
        print()
        is_fallback_local = provider == "fallback_local"
        has_fallback_text = "Sua planilha foi limpa com sucesso" in narrative_text or \
                            "narrativa detalhada" in narrative_text
        print("  [VERIFICACAO]")
        print(f"  provider_used == 'fallback_local'? {'SIM' if is_fallback_local else 'NAO (GOT: ' + provider + ')'}")
        print(f"  Texto de fallback presente?        {'SIM' if has_fallback_text else 'NAO'}")

    except Exception as e:
        elapsed = time.time() - t0
        print(f"  EXCECAO apos {elapsed:.2f}s: {e}")
    finally:
        # Restaura os singletons (as env vars serao restauradas logo depois)
        groq_mod._client   = None
        or_mod._client     = None
        nvidia_mod._client = None


def run_cenario2_via_server(dataset_id: str):
    """
    Alternativa: testa via HTTP, mas requer o servidor rodando com chaves invalidas.
    Usamos esta versao apos reiniciar o servidor (ver instrucoes ao final do script).
    """
    print()
    print("  GET /api/narrative/{dataset_id} via HTTP com chaves invalidas ...")
    print("  (dataset pode nao estar mais em memoria se o servidor foi reiniciado)")
    t0 = time.time()
    res = requests.get(f"{BASE_URL}/narrative/{dataset_id}", timeout=60)
    elapsed = time.time() - t0
    print(f"  Status: {res.status_code} em {elapsed:.2f}s")
    if res.status_code == 200:
        data = res.json()
        print(f"  provider_used: {data.get('provider_used')}")
        print(f"  narrative: {data.get('narrative', '')[:200]}")
    else:
        print(f"  Resposta: {res.text[:300]}")


# ─────────────────────────────────────────────────────────────────────────────
# Restaura chaves originais
# ─────────────────────────────────────────────────────────────────────────────

def restore_real_keys():
    """Relê o .env e restaura as env vars reais na session atual."""
    for line in open(".env"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip().strip('"')

    import app.services.ai.groq_client as groq_mod
    import app.services.ai.openrouter_client as or_mod
    import app.services.ai.nvidia_nim_client as nvidia_mod

    groq_mod._client   = None
    or_mod._client     = None
    nvidia_mod._client = None

    print()
    print("  Chaves originais restauradas (singletons resetados).")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print()
    print("Verificando servidor em http://127.0.0.1:8002 ...")
    if not check_server():
        print("  ERRO: servidor nao esta respondendo. Inicie com:")
        print("  uvicorn app.main:app --port 8002 --env-file .env")
        sys.exit(1)
    print("  Servidor OK.")
    print()

    # ── Cenario 1 ──
    dataset_id, c1_response = run_cenario1()

    # ── Cenario 2 (in-process, sem reiniciar servidor) ──
    run_cenario2_inprocess(dataset_id)

    # Restaura
    restore_real_keys()

    print()
    print(SEP)
    print("TESTES CONCLUIDOS")
    print(SEP)
