"""
Rota de teste das Etapas 4+5: sobe um CSV, roda a limpeza determinística
(Etapa 3) e manda os grupos ambíguos encontrados pro sistema de fallback
de IA resolver (Groq → Gemini → Cerebras), numa única requisição.
"""

import io

import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.data_cleaning.cleaner import run_deterministic_cleaning
from app.services.ai.text_resolution import resolve_ambiguous_groups
from app.services.ai.fallback import AllProvidersFailedError
from app.services.storage.r2_client import upload_file as r2_upload
from app.db.supabase import get_supabase_client
import uuid

router = APIRouter()


@router.post("/clean/resolve-ambiguous")
async def test_resolve_ambiguous(file: UploadFile = File(...)):
    if not file.filename.endswith((".csv", ".xlsx")):
        raise HTTPException(400, "Envie um arquivo .csv ou .xlsx")

    content = await file.read()

    dataset_id = str(uuid.uuid4())
    ext = "csv" if file.filename.endswith(".csv") else "xlsx"
    r2_path = f"originais/{dataset_id}.{ext}"
    
    try:
        r2_upload(content, r2_path, content_type=file.content_type or "application/octet-stream")
        supabase = get_supabase_client()
        supabase.table("processamentos").insert({
            "id": dataset_id,
            "nome_arquivo_original": file.filename,
            "caminho_r2_original": r2_path,
            "status": "pendente"
        }).execute()
    except Exception as e:
        raise HTTPException(500, f"Erro ao salvar arquivo/metadados: {e}")

    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(400, f"Não consegui ler o arquivo: {e}")

    cleaning_result = run_deterministic_cleaning(df)
    ambiguous_groups = cleaning_result["ambiguous_text_groups"]

    if not ambiguous_groups:
        return {
            "message": "Nenhuma ambiguidade de texto encontrada — nada pra mandar pra IA.",
            "diagnostics": cleaning_result["diagnostics"],
            "dataset_id": dataset_id,
        }

    try:
        result = resolve_ambiguous_groups(ambiguous_groups)
    except AllProvidersFailedError as e:
        # Os três provedores falharam — situação rara, mas o usuário
        # precisa de uma mensagem clara, não um erro 500 genérico.
        raise HTTPException(
            503,
            f"Não consegui resolver as ambiguidades: nenhum provedor de "
            f"IA respondeu (Groq, OpenRouter e NVIDIA NIM falharam). Detalhe: {e.errors}",
        )

    return {
        "diagnostics": cleaning_result["diagnostics"],
        "ambiguous_groups_sent": ambiguous_groups,
        "ai_decisions": result["decisions"],
        "provider_used": result["provider_used"],
        "dataset_id": dataset_id,
    }
