import os

# Carrega .env manualmente
for line in open(".env"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ[k.strip()] = v.strip().strip('"')

print("=== VERIFICANDO STATUS DOS PROVEDORES DE FALLBACK ===\n")

# Gemini
print("[1/2] Testando Gemini...")
try:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    resp = client.models.generate_content(
        model="gemini-2.0-flash",
        contents='Respond only: {"ok": true}',
        config=types.GenerateContentConfig(temperature=0, response_mime_type="application/json")
    )
    print(f"  Gemini: OK -> {resp.text.strip()}")
    gemini_ok = True
except Exception as e:
    err = str(e)
    if "RESOURCE_EXHAUSTED" in err or "429" in err:
        print(f"  Gemini: QUOTA ESGOTADA (429) - cota diaria free tier zerada")
    elif "404" in err:
        print(f"  Gemini: MODELO NAO DISPONIVEL (404)")
    else:
        print(f"  Gemini: ERRO -> {err[:200]}")
    gemini_ok = False

# Cerebras
print("\n[2/2] Testando Cerebras...")
try:
    from cerebras.cloud.sdk import Cerebras
    client = Cerebras(api_key=os.environ["CEREBRAS_API_KEY"])
    resp = client.chat.completions.create(
        model="gpt-oss-120b",
        messages=[{"role": "user", "content": 'Respond only: {"ok": true}'}],
        temperature=0
    )
    print(f"  Cerebras: OK -> {resp.choices[0].message.content.strip()[:80]}")
    cerebras_ok = True
except Exception as e:
    err = str(e)
    if "402" in err or "payment" in err.lower():
        print(f"  Cerebras: PAGAMENTO REQUERIDO (402) - conta free sem cota")
    else:
        print(f"  Cerebras: ERRO -> {err[:200]}")
    cerebras_ok = False

print()
print("=== RESULTADO ===")
print(f"  Gemini disponivel:   {'SIM' if gemini_ok else 'NAO'}")
print(f"  Cerebras disponivel: {'SIM' if cerebras_ok else 'NAO'}")

if not gemini_ok and not cerebras_ok:
    print()
    print("ATENCAO: Ambos provedores de fallback estao indisponiveis no momento.")
    print("O teste de fallback via HTTP vai retornar 503 (todos falharam),")
    print("pois os tres provedores (Groq + Gemini + Cerebras) estarao inoperantes.")
