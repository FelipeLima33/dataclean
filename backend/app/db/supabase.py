from supabase import create_client, Client
from app.core.config import settings

def get_supabase_client() -> Client:
    """
    Inicializa e retorna o cliente do Supabase utilizando 
    a URL e a KEY definidas nas configurações/ambiente.
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables.")
        
    supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    return supabase
