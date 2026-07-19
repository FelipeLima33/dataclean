import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8002/api"
CSV_PATH = r"tests\fixtures\vendas_teste_dataclean.csv"

# Step 1: POST to /clean/resolve-ambiguous
print(f"Step 1: Uploading {CSV_PATH} to /clean/resolve-ambiguous")
with open(CSV_PATH, "rb") as f:
    res = requests.post(f"{BASE_URL}/clean/resolve-ambiguous", files={"file": f})

if res.status_code != 200:
    print(f"Error {res.status_code}: {res.text}")
    sys.exit(1)

data = res.json()
dataset_id = data.get("dataset_id")
ai_decisions = data.get("ai_decisions", {})

print(f"Step 2: Received dataset_id={dataset_id}")

# Step 3: Build decisions payload
decisions = []
for col, items in ai_decisions.items():
    for item in items:
        decisions.append({
            "column": col,
            "variants": item["variants"],
            "status": "approved",
            "final_value": item["canonical"]
        })

print(f"Step 3: Built decisions payload with {len(decisions)} items")

# Step 4: POST to /clean/apply-decisions
print(f"Step 4: Applying decisions to /clean/apply-decisions")
with open(CSV_PATH, "rb") as f:
    res2 = requests.post(
        f"{BASE_URL}/clean/apply-decisions", 
        files={"file": f}, 
        data={"decisions": json.dumps(decisions), "dataset_id": dataset_id}
    )

if res2.status_code != 200:
    print(f"Error {res2.status_code}: {res2.text}")
    sys.exit(1)

data2 = res2.json()

print("\n--- JSON DE RESPOSTA FINAL (PASSO 4) ---")
print(json.dumps(data2, indent=2, ensure_ascii=False))
print("----------------------------------------")
