from fastapi import APIRouter
from app.db.supabase import get_supabase_client

router = APIRouter()

@router.get("/health")
def health_check():
    """
    Rota de saúde para verificar se a API está no ar e se a conexão
    com o Supabase pode ser instanciada corretamente.
    """
    status = {"api": "ok", "supabase": "unknown"}
    
    try:
        # Testa a instanciação do cliente
        client = get_supabase_client()
        if client:
            status["supabase"] = "ok"
    except Exception as e:
        status["supabase"] = f"error: {str(e)}"
        
    return status
