from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.db.supabase import get_supabase_client
from app.services.storage.r2_client import download_file, delete_file
import io

router = APIRouter()

@router.get("/clean/download/{dataset_id}")
async def download_cleaned_file(dataset_id: str):
    supabase = get_supabase_client()
    response = supabase.table("processamentos").select("caminho_r2_limpo").eq("id", dataset_id).execute()
    
    if not response.data or not response.data[0].get("caminho_r2_limpo"):
        raise HTTPException(404, "Arquivo limpo não encontrado")
    
    caminho = response.data[0]["caminho_r2_limpo"]
    
    try:
        file_bytes = download_file(caminho)
        return StreamingResponse(
            io.BytesIO(file_bytes),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={dataset_id}_limpo.csv"
            }
        )
    except Exception as e:
        raise HTTPException(500, f"Erro ao baixar o arquivo do armazenamento: {e}")

@router.post("/admin/cleanup-old-files")
async def cleanup_old_files():
    """
    Remove arquivos do R2 de processamentos com mais de 30 dias.
    Idealmente acionado por um cron job em produção.
    """
    supabase = get_supabase_client()
    
    # Busca registros onde data_processamento < now() - 30 days
    # Supabase syntax for < now() - interval '30 days' using lte
    from datetime import datetime, timedelta, timezone
    thirty_days_ago = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    
    response = supabase.table("processamentos") \
        .select("id, caminho_r2_original, caminho_r2_limpo") \
        .lte("data_processamento", thirty_days_ago) \
        .neq("status", "arquivado") \
        .execute()
        
    registros = response.data
    deleted_count = 0
    
    for row in registros:
        r2_orig = row.get("caminho_r2_original")
        r2_limpo = row.get("caminho_r2_limpo")
        
        try:
            if r2_orig:
                delete_file(r2_orig)
            if r2_limpo:
                delete_file(r2_limpo)
                
            # Atualiza no Supabase
            supabase.table("processamentos").update({
                "caminho_r2_original": None,
                "caminho_r2_limpo": None,
                "status": "arquivado"
            }).eq("id", row["id"]).execute()
            
            deleted_count += 1
        except Exception as e:
            print(f"Erro ao limpar arquivos do registro {row['id']}: {e}")
            
    return {"message": f"Limpeza concluída. {deleted_count} registros processados e seus arquivos deletados."}
