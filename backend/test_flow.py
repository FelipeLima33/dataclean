import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8002/api"
CSV_PATH = r"D:\dawnloads\vendas_teste_dataclean.csv"

# 1. Hit resolve-ambiguous
with open(CSV_PATH, "rb") as f:
    res = requests.post(f"{BASE_URL}/clean/resolve-ambiguous", files={"file": f})

if res.status_code != 200:
    print(f"Error {res.status_code}: {res.text}")
    sys.exit(1)

data = res.json()

print("--- JSON RESPONSE ---")
print(json.dumps(data, indent=2))
print("---------------------")

dataset_id = data.get("dataset_id")
ai_decisions = data.get("ai_decisions", {})

# 2. Build decisions for apply-decisions
decisions = []
for col, items in ai_decisions.items():
    for item in items:
        decisions.append({
            "column": col,
            "variants": item["variants"],
            "status": "approved",
            "final_value": item["canonical"]
        })

print("Applying decisions:", decisions)

# 3. Hit apply-decisions
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
download_url = data2.get("download_url")

# 4. Download file
res_dl = requests.get(f"http://127.0.0.1:8002/api{download_url}")
if res_dl.status_code == 200:
    with open("vendas_teste_resultado_v2.csv", "wb") as f:
        f.write(res_dl.content)
    print("Downloaded vendas_teste_resultado_v2.csv successfully!")
else:
    print(f"Error downloading: {res_dl.status_code} {res_dl.text}")
