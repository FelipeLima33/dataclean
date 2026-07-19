from fastapi import APIRouter, HTTPException
from app.services.storage.memory_store import get_dataset
from app.services.charts.chart_engine import get_charts_plan
from app.services.charts.chart_data import build_chart_data

router = APIRouter()

@router.get("/charts/{dataset_id}")
async def get_charts(dataset_id: str):
    """
    Retorna os gráficos recomendados para o dataset limpo, 
    já processados e formatados para o Recharts.
    """
    data = get_dataset(dataset_id)
    if not data:
        raise HTTPException(404, "Dataset não encontrado ou expirado.")
        
    df, diagnostics = data
    
    # Roda o motor de decisão para decidir quais gráficos exibir
    plan = get_charts_plan(df)
    
    # Processa cada gráfico para gerar o payload JSON final
    charts_ready = []
    for chart_plan in plan:
        chart_ready = build_chart_data(chart_plan, df, diagnostics)
        # Repassa a prioridade
        chart_ready["priority"] = chart_plan["priority"]
        charts_ready.append(chart_ready)
        
    return {"charts": charts_ready}
