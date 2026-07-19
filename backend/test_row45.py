import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8002/api"
CSV_PATH = r"tests\fixtures\vendas_teste_dataclean.csv"

# Step 1 — resolve-ambiguous
print("Step 1: resolve-ambiguous")
with open(CSV_PATH, "rb") as f:
    res = requests.post(f"{BASE_URL}/clean/resolve-ambiguous", files={"file": f})
if res.status_code != 200:
    print(f"Error {res.status_code}: {res.text}")
    sys.exit(1)
data = res.json()
dataset_id = data["dataset_id"]
ai_decisions = data.get("ai_decisions", {})
print(f"  dataset_id = {dataset_id}")

# Step 2 — build decisions (all approved)
decisions = []
for col, items in ai_decisions.items():
    for item in items:
        decisions.append({
            "column": col,
            "variants": item["variants"],
            "status": "approved",
            "final_value": item["canonical"]
        })
print(f"  {len(decisions)} decisions built (all approved)")

# Step 3 — apply-decisions
print("Step 2: apply-decisions")
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

print("\n--- apply_report ---")
print(json.dumps(data2["apply_report"], indent=2, ensure_ascii=False))

# Step 4 — download final CSV and inspect row id=45
print("\nStep 3: download CSV and inspect row id=45")
res_dl = requests.get(f"http://127.0.0.1:8002/api/clean/download/{dataset_id}")
if res_dl.status_code != 200:
    print(f"Download error: {res_dl.status_code}")
    sys.exit(1)

# Save and parse
with open("resultado_test_v3.csv", "wb") as f:
    f.write(res_dl.content)

import pandas as pd, io
df = pd.read_csv(io.BytesIO(res_dl.content))

row45 = df[df["id"] == 45]
if row45.empty:
    print("Row id=45 NOT FOUND in output!")
else:
    print("\nRow id=45 in final CSV:")
    print(row45[["id", "quantidade", "valor_unitario", "valor_total"]].to_string(index=False))
    vt = row45["valor_total"].values[0]
    qt = row45["quantidade"].values[0]
    vu = row45["valor_unitario"].values[0]
    expected = qt * vu
    print(f"\n  quantidade      = {qt}")
    print(f"  valor_unitario  = {vu}")
    print(f"  valor_total     = {vt}")
    print(f"  qt * vu         = {expected}")
    print(f"  valor_total == 2697.0? {'✅ YES' if abs(vt - 2697.0) < 0.001 else '❌ NO (got ' + str(vt) + ')'}")
    print(f"  valor_total == qt*vu?  {'✅ YES' if abs(vt - expected) < 0.001 else '❌ NO'}")
