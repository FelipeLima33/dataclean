"""
Rota de teste da Etapa 3: sobe um CSV, roda a limpeza determinística,
devolve o diagnóstico em JSON. Serve pra validar o pipeline isoladamente,
sem depender do frontend nem de storage/banco (que ainda não foram
integrados).
"""

import io

import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.data_cleaning.cleaner import run_deterministic_cleaning
from app.core.serialization import safe_json_records

router = APIRouter()


@router.post("/clean/test")
async def test_cleaning(file: UploadFile = File(...)):
    if not file.filename.endswith((".csv", ".xlsx")):
        raise HTTPException(400, "Envie um arquivo .csv ou .xlsx")

    content = await file.read()

    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(400, f"Não consegui ler o arquivo: {e}")

    result = run_deterministic_cleaning(df)

    # DataFrame não é serializável direto em JSON — NaN seria rejeitado pelo
    # encoder padrão do Python. safe_json_records substitui NaN/inf por None.
    preview = safe_json_records(result["cleaned_df"], n=10)

    return {
        "diagnostics": result["diagnostics"],
        "outliers": result["outliers"],
        "ambiguous_text_groups": result["ambiguous_text_groups"],
        "cleaned_preview": preview,
    }
