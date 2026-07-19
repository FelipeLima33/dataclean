import requests
import json
import time
from app.db.supabase import get_supabase_client
from app.services.storage.r2_client import download_file

BASE_URL = "http://127.0.0.1:8000/api"

print("--- INICIANDO TESTE END-TO-END (Simulando Frontend) ---")

# 1. Upload Inicial
print("\n[1] Testando Upload Inicial (/clean/resolve-ambiguous)...")
with open("test_data.csv", "rb") as f:
    files = {"file": ("test_data.csv", f, "text/csv")}
    res = requests.post(f"{BASE_URL}/clean/resolve-ambiguous", files=files)

print("Status:", res.status_code)
if res.status_code != 200:
    print(res.text)
    
data = res.json()
dataset_id = data.get("dataset_id")
print("Dataset ID gerado:", dataset_id)

# 2. Verifica Supabase após upload
print("\n[2] Verificando Supabase após upload inicial...")
supabase = get_supabase_client()
row = supabase.table("processamentos").select("*").eq("id", dataset_id).execute()
print("Registro no Supabase:")
print(json.dumps(row.data, indent=2))

time.sleep(2)

# 3. Apply Decisions
print("\n[3] Testando Apply Decisions (/clean/apply-decisions)...")
decisions = [
    {
        "column": "nome",
        "variants": ["João", "joao"],
        "status": "approved",
        "final_value": "João"
    }
]

with open("test_data.csv", "rb") as f:
    files = {"file": ("test_data.csv", f, "text/csv")}
    data_form = {
        "decisions": json.dumps(decisions),
        "dataset_id": dataset_id
    }
    res2 = requests.post(f"{BASE_URL}/clean/apply-decisions", files=files, data=data_form)

print("Status:", res2.status_code)
if res2.status_code != 200:
    print(res2.text)
data2 = res2.json()
download_url = data2.get("download_url")
print("Download URL gerada:", download_url)

# 4. Verifica Supabase após apply
print("\n[4] Verificando Supabase após apply-decisions...")
row2 = supabase.table("processamentos").select("*").eq("id", dataset_id).execute()
print("Registro no Supabase (Atualizado):")
print(json.dumps(row2.data, indent=2))

# 5. Testa o Download
print("\n[5] Testando Rota de Download...")
res_dl = requests.get(f"http://127.0.0.1:8000/api{download_url}")
print("Status do Download:", res_dl.status_code)
if res_dl.status_code == 200:
    print("Download bem sucedido! Tamanho em bytes:", len(res_dl.content))
else:
    print("Erro no download:", res_dl.text)

print("\n--- TESTE CONCLUÍDO ---")
