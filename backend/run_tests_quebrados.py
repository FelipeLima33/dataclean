import os
import requests
import json

url = "http://127.0.0.1:8002/api/clean/test"
dir_path = r"d:\Data Cleaner\backend\tests\fixtures\testes_quebrados"

files = sorted(os.listdir(dir_path))
print(f"Encontrados {len(files)} arquivos na pasta:")
for f in files:
    print(f" - {f}")

for f_name in files:
    f_path = os.path.join(dir_path, f_name)
    print(f"\n======================================")
    print(f"Testando arquivo: {f_name}")
    print(f"======================================")
    try:
        with open(f_path, "rb") as f:
            res = requests.post(url, files={"file": (f_name, f)})
        print(f"Status Code: {res.status_code}")
        try:
            body = res.json()
            print("Response Body (JSON):")
            print(json.dumps(body, indent=2, ensure_ascii=False))
        except Exception:
            print("Response Body (Text):")
            print(res.text)
    except Exception as e:
        print(f"Erro ao enviar requisição: {e}")
