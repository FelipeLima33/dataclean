import uuid
import pandas as pd
from typing import Dict, Optional, Tuple

# Em-memory store temporário para datasets já limpos e seus diagnósticos
_datasets: Dict[str, Tuple[pd.DataFrame, dict]] = {}

def save_dataset(df: pd.DataFrame, diagnostics: dict = None, dataset_id: str = None) -> str:
    """Salva um DataFrame e seus diagnósticos em memória e retorna o UUID."""
    if not dataset_id:
        dataset_id = str(uuid.uuid4())
    _datasets[dataset_id] = (df, diagnostics or {})
    return dataset_id

def get_dataset(dataset_id: str) -> Optional[Tuple[pd.DataFrame, dict]]:
    """Retorna a tupla (DataFrame, diagnostics) correspondente ao UUID, ou None se não existir."""
    return _datasets.get(dataset_id)
