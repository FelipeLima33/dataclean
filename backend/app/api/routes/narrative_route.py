from fastapi import APIRouter, HTTPException
from app.services.storage.memory_store import get_dataset
from app.services.charts.chart_engine import get_charts_plan
from app.services.ai.narrative import generate_narrative
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/narrative/{dataset_id}")
async def get_narrative(dataset_id: str):
    """
    Gera o parágrafo explicativo da limpeza via IA.
    """
    data = get_dataset(dataset_id)
    if not data:
        raise HTTPException(404, "Dataset não encontrado ou expirado.")
        
    df, diagnostics = data
    
    # Roda o motor de decisão para extrair contexto de gráficos (metadata)
    plan = get_charts_plan(df)
    
    try:
        narrative_text, provider_name = generate_narrative(diagnostics, plan)
        return {
            "narrative": narrative_text,
            "provider_used": provider_name
        }
    except Exception as e:
        logger.error(f"Erro ao gerar narrativa: {e}")
        return {
            "narrative": "Sua planilha foi limpa com sucesso. Não foi possível gerar a narrativa detalhada no momento devido a instabilidades na IA.",
            "provider_used": "fallback_local"
        }
