import pandas as pd
import numpy as np

def build_bar_chart(df: pd.DataFrame, col: str) -> dict:
    # Contagem de categorias top 15
    counts = df[col].value_counts().head(15)
    data = [{"name": str(idx), "value": int(val)} for idx, val in counts.items()]
    return {"data": data}

def build_histogram(df: pd.DataFrame, col: str) -> dict:
    s = df[col].dropna()
    if s.empty:
        return {"data": []}
    
    # 10 bins
    counts, bin_edges = np.histogram(s, bins=10)
    data = []
    for i in range(len(counts)):
        bin_start = float(bin_edges[i])
        bin_end = float(bin_edges[i+1])
        label = f"{bin_start:.1f} - {bin_end:.1f}"
        data.append({"name": label, "value": int(counts[i])})
    
    return {"data": data}

def build_boxplot(df: pd.DataFrame, col: str) -> dict:
    s = df[col].dropna()
    if s.empty:
        return {"data": []}
        
    q1 = float(s.quantile(0.25))
    median = float(s.median())
    q3 = float(s.quantile(0.75))
    iqr = q3 - q1
    min_val = float(s.min())
    max_val = float(s.max())
    
    # Lower/upper fences
    lower_fence = float(max(min_val, q1 - 1.5 * iqr))
    upper_fence = float(min(max_val, q3 + 1.5 * iqr))
    
    # Outliers
    outliers = s[(s < lower_fence) | (s > upper_fence)].tolist()
    
    return {
        "data": [{
            "name": col,
            "min": min_val,
            "q1": q1,
            "median": median,
            "q3": q3,
            "max": max_val,
            "lower_fence": lower_fence,
            "upper_fence": upper_fence,
            "outliers": [float(x) for x in outliers]
        }]
    }

def build_heatmap_correlacao(df: pd.DataFrame, columns: list) -> dict:
    corr = df[columns].corr().round(2)
    # Transforma em array para o Recharts
    data = []
    for col1 in columns:
        for col2 in columns:
            data.append({
                "x": col1,
                "y": col2,
                "value": float(corr.loc[col1, col2]) if pd.notna(corr.loc[col1, col2]) else 0
            })
    return {"data": data, "columns": columns}

def build_linha_temporal(df: pd.DataFrame, col: str) -> dict:
    s = pd.to_datetime(df[col], errors='coerce').dropna()
    if s.empty:
        return {"data": []}
        
    # Agrupa por mês ou dia
    counts = s.dt.to_period('M').value_counts().sort_index()
    # Se der muito poucos pontos (ex: < 3 meses), tenta agrupar por dia
    if len(counts) < 3:
        counts = s.dt.to_period('D').value_counts().sort_index()
        
    data = [{"name": str(idx), "value": int(val)} for idx, val in counts.items()]
    return {"data": data}

def build_grafico_qualidade(df: pd.DataFrame, col: str) -> dict:
    total = len(df)
    nulos = int(df[col].isnull().sum())
    validos = total - nulos
    
    data = [
        {"name": "Válidos", "value": validos},
        {"name": "Ausentes", "value": nulos}
    ]
    return {"data": data, "percentual_nulo": round((nulos/total)*100, 1) if total > 0 else 0}

def build_chart_data(plan: dict, df: pd.DataFrame, diagnostics: dict = None) -> dict:
    """Dado o plano de um gráfico e o df, gera a estrutura de dados JSON final."""
    ctype = plan["type"]
    col = plan.get("column")
    
    result = {
        "id": f"{ctype}_{col if col else 'global'}",
        "type": ctype,
        "title": f"Gráfico de {ctype.replace('_', ' ').title()}",
        "column": col
    }
    
    if ctype == "barras":
        result.update(build_bar_chart(df, col))
        result["title"] = f"Distribuição de {col}"
    elif ctype == "histograma":
        result.update(build_histogram(df, col))
        result["title"] = f"Distribuição de {col}"
    elif ctype == "boxplot":
        result.update(build_boxplot(df, col))
        result["title"] = f"Boxplot de {col}"
    elif ctype == "heatmap_correlacao":
        result.update(build_heatmap_correlacao(df, plan["columns"]))
        result["title"] = "Correlação Numérica"
    elif ctype == "linha_temporal":
        result.update(build_linha_temporal(df, col))
        result["title"] = f"Linha do Tempo: {col}"
    elif ctype == "grafico_qualidade_dados":
        result.update(build_grafico_qualidade(df, col))
        result["title"] = f"Qualidade: {col}"
    elif ctype == "before_after":
        # Usa os dados de diagnostics enviados na requisição ou obtidos globalmente
        if diagnostics:
            duplicatas = diagnostics.get("duplicates_removed", 0)
            inconsistencias = diagnostics.get("text_inconsistencies_resolved", 0)
            ausentes = diagnostics.get("missing_values_filled", 0)
            
            data = [
                {"name": "Duplicatas", "resolvidos": duplicatas},
                {"name": "Inconsistências", "resolvidos": inconsistencias},
                {"name": "Valores Ausentes", "resolvidos": ausentes}
            ]
            result["data"] = data
            result["title"] = "Antes vs Depois da Limpeza"
        else:
            result["data"] = []
    elif ctype in ("mapa", "wordcloud"):
        result["data"] = [] # placeholders
        result["title"] = f"{ctype.title()}: {col}"
        
    return result
