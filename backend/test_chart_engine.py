"""
Testa as 3 correções do chart_engine com o dataset de vendas real.
"""
import io
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from app.services.charts.chart_engine import get_charts_plan

# Dataset simulado (mesmas colunas do vendas_teste_dataclean.csv)
dados = {
    "id":            list(range(1, 11)),                           # identificador — deve ser pulado
    "data_venda":    ["15/01/2024","2024-02-10","10-03-2024",
                      "20/04/2024","2024-05-05","30/06/2024",
                      "12/07/2024","2024-08-22","09-09-2024","2024-10-01"],
    "nome_cliente":  ["Alice","Bob","Carlos","Diana","Eve",
                      "Félix","Gabi","Heitor","Iara","João"],
    "cidade":        ["São Paulo","Rio de Janeiro","Belém","Belém",
                      "Marabá","Santarém","Ananindeua","SP","RJ","São Paulo"],
    "produto":       ["Notebook Dell","Monitor LG 24Pol","Notebook Dell","Mouse Logitech",
                      "Monitor LG 24Pol","Notebook Dell","Mouse Logitech","Teclado",
                      "Notebook Dell","Monitor LG 24Pol"],
    "valor_unitario":[3500,800,3500,120,800,3500,120,200,3500,800],
    "valor_total":   [3500,800,7000,120,1600,3500,240,200,10500,800],
    "comentario":    ["Ótima compra, produto chegou rápido",
                      "Boa qualidade, recomendo",
                      "Excelente atendimento e produto",
                      "Produto ok, demora na entrega",
                      "Recomendo fortemente, excelente custo-benefício",
                      "Muito bom, superou expectativas",
                      "Produto chegou com defeito, trocou rápido",
                      "Ótimo, comprei novamente",
                      "Perfeito, exatamente o que esperava",
                      "Qualidade duvidosa, mas preço justo"],
}

df = pd.DataFrame(dados)

plan = get_charts_plan(df)

print("\n=== PLANO DE GRÁFICOS GERADO ===")
for p in plan:
    col = p.get("column", p.get("columns", "(global)"))
    print(f"  tipo={p['type']:25s} | coluna={col}")

# --- Assertions ---
tipos = {p.get("column"): p["type"] for p in plan if "column" in p}

print("\n=== VALIDACOES ===")

# (a) Nenhum gráfico para 'id'
assert "id" not in tipos, "FALHOU: coluna 'id' nao deveria gerar grafico"
print("OK (a) Coluna 'id' ignorada corretamente")

# (b) comentario => wordcloud
assert tipos.get("comentario") == "wordcloud", \
    f"FALHOU: esperado 'wordcloud' para comentario, obteve '{tipos.get('comentario')}'"
print("OK (b) Coluna 'comentario' classificada como wordcloud")

# (c) data_venda => linha_temporal
assert tipos.get("data_venda") == "linha_temporal", \
    f"FALHOU: esperado 'linha_temporal' para data_venda, obteve '{tipos.get('data_venda')}'"
print("OK (c) Coluna 'data_venda' classificada como linha_temporal")

print("\nTodos os testes passaram!\n")
