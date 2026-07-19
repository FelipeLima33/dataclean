"""
Rota da Etapa 6: recebe o arquivo original + as decisões do usuário
(vindas da tela de Sugestões) e devolve o dataset final, já com as
substituições aprovadas aplicadas.
"""

import io
import json

import pandas as pd
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.services.data_cleaning.cleaner import run_deterministic_cleaning
from app.services.data_cleaning.apply_decisions import apply_user_decisions
from app.services.storage.r2_client import upload_file as r2_upload
from app.db.supabase import get_supabase_client
from app.core.serialization import safe_json_records

router = APIRouter()


@router.post("/clean/apply-decisions")
async def apply_decisions(
    file: UploadFile = File(...),
    decisions: str = Form(...),  # JSON string, vem do FormData do frontend
    dataset_id: str = Form(...), # ID recebido na etapa 1
):
    if not file.filename.endswith((".csv", ".xlsx")):
        raise HTTPException(400, "Envie um arquivo .csv ou .xlsx")

    try:
        parsed_decisions = json.loads(decisions)
        print(json.dumps(parsed_decisions, indent=2, ensure_ascii=False))
    except json.JSONDecodeError:
        raise HTTPException(400, "Campo 'decisions' não é um JSON válido")

    content = await file.read()
    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(400, f"Não consegui ler o arquivo: {e}")

    # Refaz a limpeza determinística (duplicatas, ausentes, outliers)
    # pra garantir consistência — o frontend não manda o df intermediário
    cleaning_result = run_deterministic_cleaning(df)

    # Aplica só as decisões que o usuário aprovou/editou na tela 3
    df_final, apply_report = apply_user_decisions(
        cleaning_result["cleaned_df"], parsed_decisions
    )

    remaining_ambiguous = sum(
        1
        for d in parsed_decisions
        if d["status"] == "rejected"
    )

    final_diagnostics = {
        **cleaning_result["diagnostics"],
        "text_inconsistencies_resolved": len(parsed_decisions) - remaining_ambiguous,
        "text_inconsistencies_kept_as_is": remaining_ambiguous,
    }

    from app.services.storage.memory_store import save_dataset
    save_dataset(df_final, final_diagnostics, dataset_id=dataset_id)

    # Faz o upload do arquivo limpo pro R2
    csv_buffer = io.BytesIO()
    df_final.to_csv(csv_buffer, index=False)
    r2_path = f"limpos/{dataset_id}_limpo.csv"
    
    try:
        r2_upload(csv_buffer.getvalue(), r2_path, content_type="text/csv")
        supabase = get_supabase_client()
        supabase.table("processamentos").update({
            "caminho_r2_limpo": r2_path,
            "diagnostico_json": final_diagnostics,
            "status": "concluido"
        }).eq("id", dataset_id).execute()
    except Exception as e:
        print(f"Aviso: Erro ao salvar arquivo limpo no R2 / Supabase: {e}")

    print(json.dumps(apply_report, indent=2, ensure_ascii=False))
    return {
        "diagnostics": final_diagnostics,
        "apply_report": apply_report,
        "cleaned_preview": safe_json_records(df_final, n=10),
        "rows_total": len(df_final),
        "dataset_id": dataset_id,
        "download_url": f"/clean/download/{dataset_id}",
    }
