import asyncio
import os
from app.services.ai.narrative import generate_narrative

for line in open(".env"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ[k.strip()] = v.strip().strip('"')

diagnostics = {
    "rows_before": 78,
    "duplicates_removed": 6,
    "missing_values_filled": 24,
    "outliers_flagged": 5, # <-- O nome do campo real da API
    "text_inconsistencies_resolved": 10,
}

charts_plan = [
    {"type": "boxplot", "column": "valor_unitario"},
    {"type": "boxplot", "column": "valor_total"},
    {"type": "mapa",    "column": "cidade"},
]

narrative, provider = generate_narrative(diagnostics, charts_plan)
print("\n=== NARRATIVA GERADA ===")
print(narrative)
print("========================\n")
