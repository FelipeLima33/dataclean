import pandas as pd
import numpy as np

def tem_outliers(series: pd.Series) -> bool:
    """Verifica se há outliers usando o método IQR."""
    s = series.dropna()
    if len(s) < 10:
        return False
    Q1 = s.quantile(0.25)
    Q3 = s.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return ((s < lower_bound) | (s > upper_bound)).any()

def eh_coluna_geografica(coluna: str) -> bool:
    """Verifica se a coluna indica localização baseada no nome."""
    keywords = ['cidade', 'estado', 'uf', 'país', 'pais', 'cep', 'endereço', 'endereco', 'city', 'state', 'country']
    col_lower = coluna.lower()
    return any(kw in col_lower for kw in keywords)

def eh_coluna_identificadora(coluna: str, series: pd.Series) -> bool:
    """
    Retorna True se a coluna parece ser um identificador (ID, chave primária).
    Regras:
      - Colunas datetime nunca são identificadoras.
      - O NOME da coluna sugere ID (id, _id, id_, _key, codigo, cod_): sempre skip.
      - Coluna NUMÉRICA com cardinalidade 100%: também é ID (ex: id sequencial int).
      - Colunas string/texto com 100% unique NÃO são consideradas ID — podem ser
        nomes, comentários, datas como string, etc.
    """
    # Colunas datetime nunca são IDs
    if pd.api.types.is_datetime64_any_dtype(series):
        return False

    col_lower = coluna.lower()
    nome_sugere_id = (
        col_lower == "id"
        or col_lower.endswith("_id")
        or col_lower.startswith("id_")
        or col_lower.endswith("_key")
        or col_lower == "codigo"
        or col_lower.startswith("cod_")
    )
    if nome_sugere_id:
        return True

    # Para colunas numéricas, cardinalidade 100% indica ID sequencial
    if pd.api.types.is_numeric_dtype(series):
        s = series.dropna()
        if len(s) > 0 and s.nunique() == len(s):
            return True

    return False


def eh_texto_livre(coluna: str, series: pd.Series) -> bool:
    """
    Verifica se a coluna é de texto livre (descrições, comentários).
    Usa duas heurísticas combinadas:
      - Nome da coluna sugere texto livre (comentario, descricao, obs, etc.)
      - OU: cardinalidade alta (>50% únicos) E comprimento médio > 15 chars.
    """
    if not pd.api.types.is_object_dtype(series) and not pd.api.types.is_string_dtype(series):
        return False
    s = series.dropna().astype(str)
    if len(s) == 0:
        return False

    # Heurística por nome da coluna
    col_lower = coluna.lower()
    nome_sugere_texto = any(kw in col_lower for kw in [
        'comentario', 'comentário', 'comment', 'descricao', 'descrição',
        'description', 'observacao', 'observação', 'obs', 'nota', 'note',
        'feedback', 'mensagem', 'message', 'texto', 'text', 'detalhe', 'detail'
    ])

    avg_length = s.str.len().mean()
    unique_ratio = s.nunique() / len(s)

    # Texto livre por nome OU por métricas (avg > 15 chars e >50% únicos)
    return nome_sugere_texto or (avg_length > 15 and unique_ratio > 0.5)

def _normalizar_datas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tenta converter colunas object/string para datetime.
    Se a conversão funcionar em pelo menos 80% das linhas não-nulas,
    substitui a coluna original pelo resultado normalizado (formato ISO único).
    """
    formatos = [
        "%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y",
        "%d/%m/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S",
        "%d/%m/%y", "%y-%m-%d",
    ]
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            continue  # já está correta
        if not (pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col])):
            continue

        s = df[col].dropna().astype(str)
        if s.empty:
            continue

        # Tenta cada formato explícito primeiro (evita falsos positivos)
        convertido = None
        for fmt in formatos:
            try:
                tentativa = pd.to_datetime(df[col], format=fmt, errors="coerce")
                taxa_sucesso = tentativa.notna().sum() / max(df[col].notna().sum(), 1)
                if taxa_sucesso >= 0.8:
                    convertido = tentativa
                    break
            except Exception:
                continue

        # Fallback: deixa o pandas inferir cada valor individualmente (format='mixed')
        if convertido is None:
            try:
                tentativa = pd.to_datetime(df[col], format="mixed", dayfirst=True, errors="coerce")
                taxa_sucesso = tentativa.notna().sum() / max(df[col].notna().sum(), 1)
                if taxa_sucesso >= 0.8:
                    convertido = tentativa
            except Exception:
                pass

        if convertido is not None:
            df = df.copy()
            df[col] = convertido

    return df

def escolher_grafico(coluna: str, df: pd.DataFrame) -> str:
    """Decide qual gráfico faz mais sentido para a coluna."""
    series = df[coluna]

    # 0. Identificadores — nunca geram gráfico
    if eh_coluna_identificadora(coluna, series):
        return "__skip__"

    # 1. Qualidade de dados (muitos nulos)
    if series.isnull().mean() > 0.3:
        return "grafico_qualidade_dados"
        
    # 2. Textos longos / texto livre
    if eh_texto_livre(coluna, series):
        return "wordcloud"
        
    # 3. Geográfico
    if eh_coluna_geografica(coluna):
        return "mapa"
        
    # 4. Temporal (já normalizado por _normalizar_datas)
    if pd.api.types.is_datetime64_any_dtype(series):
        return "linha_temporal"
            
    # 5. Numérico
    if pd.api.types.is_numeric_dtype(series):
        if tem_outliers(series):
            return "boxplot"
        return "histograma"
        
    # 6. Categórico
    if series.nunique() <= 15:
        return "barras"
        
    # Fallback se não for nada disso
    return "barras"

# Priorização para definir a ordem na UI
PRIORITY = {
    "grafico_qualidade_dados": 1,
    "boxplot": 3,
    "histograma": 4,
    "barras": 5,
    "heatmap_correlacao": 6,
    "linha_temporal": 7,
    "mapa": 8,
    "wordcloud": 9,
}

def get_charts_plan(df: pd.DataFrame) -> list:
    """
    Avalia todas as colunas do dataset e devolve uma lista de planos de gráficos.
    Inclui heatmap e before_after separadamente, e prioriza a lista final.
    """
    charts = []
    
    # ── Pré-processamento: normalizar colunas de data ──────────────────────
    df = _normalizar_datas(df)
    
    # Avalia coluna a coluna
    for col in df.columns:
        chart_type = escolher_grafico(col, df)
        if chart_type == "__skip__":
            continue  # coluna identificadora — ignora
        charts.append({
            "type": chart_type,
            "column": col,
            "priority": PRIORITY.get(chart_type, 99)
        })
        
    # Adiciona Heatmap de correlação se houver múltiplas colunas numéricas
    # (exclui colunas identificadoras que podem ser int sequencial)
    id_cols = {
        col for col in df.columns
        if not pd.api.types.is_datetime64_any_dtype(df[col])
        and eh_coluna_identificadora(col, df[col])
    }
    num_cols = [
        c for c in df.select_dtypes(include=[np.number]).columns.tolist()
        if c not in id_cols
    ]
    if len(num_cols) >= 2:
        charts.append({
            "type": "heatmap_correlacao",
            "columns": num_cols,
            "priority": PRIORITY["heatmap_correlacao"]
        })
        
    # Adiciona o gráfico de Antes/Depois (que será sempre 2, injetado na rota com dados de diagnóstico)
    charts.append({
        "type": "before_after",
        "priority": 2
    })
    
    # Ordena por prioridade
    charts.sort(key=lambda x: x["priority"])
    
    return charts
