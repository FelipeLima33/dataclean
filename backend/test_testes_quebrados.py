import requests
import os

pasta = r"d:\Data Cleaner\backend\tests\fixtures\testes_quebrados"
arquivos = sorted(os.listdir(pasta))

for nome_arquivo in arquivos:
    caminho = os.path.join(pasta, nome_arquivo)
    print(f"\n{'='*50}")
    print(f"TESTANDO: {nome_arquivo}")
    print('='*50)
    try:
        with open(caminho, "rb") as f:
            resp = requests.post(
                "http://localhost:8002/api/clean/test",
                files={"file": (nome_arquivo, f)},
                timeout=10,
            )
        print(f"STATUS: {resp.status_code}")
        print(f"RESPOSTA: {resp.text[:1000]}")
    except requests.exceptions.Timeout:
        print("RESULTADO: TIMEOUT (mais de 10s sem resposta)")
    except Exception as e:
        print(f"RESULTADO: ERRO NO SCRIPT - {e}")

print(f"\n{'='*50}")
print("TODOS OS TESTES CONCLUÍDOS")
print('='*50)
