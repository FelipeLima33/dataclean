from .fallback import call_ai_with_fallback

def generate_narrative(diagnostics: dict, charts_plan: list) -> tuple[str, str]:
    """
    Gera um parágrafo humano resumindo a limpeza do dataset.
    Usa o sistema de fallback existente.
    """
    
    # Extração das métricas
    rows_before = diagnostics.get("rows_before", 0)
    duplicates = diagnostics.get("duplicates_removed", 0)
    missing = diagnostics.get("missing_values_filled", 0)
    # Outliers são DETECTADOS e sinalizados, nunca removidos/ajustados automaticamente.
    # O campo pode vir como "outliers_flagged", "outliers_detected" ou "outliers_adjusted" (legado).
    outliers = diagnostics.get("outliers_flagged",
               diagnostics.get("outliers_detected",
               diagnostics.get("outliers_adjusted", 0)))
    inconsistencies = diagnostics.get("text_inconsistencies_resolved", 0)

    # Extração de insights dos gráficos
    # Para outliers, coletamos as colunas em que foram detectados (evitar duplicar
    # a informação: a métrica `outliers` já conta o total, aqui só listamos as colunas).
    outlier_columns: list[str] = []
    quality_issues: list[str] = []
    geo_columns: list[str] = []

    for plan in charts_plan:
        c_type = plan.get("type")
        c_col = plan.get("column", plan.get("columns", ""))
        if c_type == "boxplot" and c_col:
            outlier_columns.append(f"'{c_col}'")
        elif c_type == "grafico_qualidade_dados" and c_col:
            quality_issues.append(f"A coluna '{c_col}' tinha muitos dados ausentes (mais de 30%).")
        elif c_type == "mapa" and c_col:
            geo_columns.append(f"'{c_col}'")

    # Linha de contexto de outliers para o prompt — usada apenas quando outliers > 0
    if outlier_columns:
        outlier_context = (
            f"Os {outliers} outliers foram detectados nas colunas "
            + ", ".join(outlier_columns) + "."
        )
    elif outliers > 0:
        outlier_context = f"Foram detectados {outliers} outliers no dataset."
    else:
        outlier_context = "Nenhum outlier foi detectado no dataset."

    other_insights: list[str] = quality_issues
    if geo_columns:
        other_insights.append(
            "O dataset possui dados geográficos relevantes nas colunas "
            + ", ".join(geo_columns) + "."
        )
    other_chart_info = " ".join(other_insights) if other_insights else ""

    prompt = f"""Você é um analista de dados especialista e gentil.
O sistema DataClean acabou de processar e limpar uma planilha enviada por um usuário (dono de um pequeno negócio que não é técnico).
Seu objetivo é escrever um RESUMO EXECUTIVO curto (apenas 1 parágrafo com 3 a 5 frases), em português, explicando o que foi feito na planilha dele.

Aqui estão os dados numéricos da limpeza:
- Linhas originais: {rows_before}
- Linhas duplicadas removidas: {duplicates}
- Valores ausentes preenchidos estatisticamente: {missing}
- Outliers (valores extremos) DETECTADOS e sinalizados para revisão: {outliers}
- Inconsistências de texto corrigidas pela IA e pelo usuário: {inconsistencies}

Contexto sobre outliers (LEIA COM ATENÇÃO):
{outlier_context}
{other_chart_info}

REGRAS OBRIGATÓRIAS:
1. Cite os números específicos fornecidos acima, mas de forma fluida.
   Exemplo: "Removemos {duplicates} duplicatas e preenchemos {missing} valores vazios."
2. REGRA ESPECIAL SOBRE OUTLIERS — Esta regra prevalece sobre qualquer outra:
   - Outliers são APENAS detectados e sinalizados; NUNCA são removidos ou ajustados automaticamente.
   - Se outliers > 0: descreva-os como "identificamos X outlier(s) nas colunas Y, que ficam sinalizados para sua revisão manual" (ou frase equivalente). NÃO diga que foram ajustados, corrigidos, removidos ou que "não foram necessários ajustes".
   - Se outliers == 0: simplesmente não mencione outliers, ou diga "nenhum outlier foi detectado".
   - NUNCA contradiga essa regra na mesma frase ou parágrafo (ex.: NÃO escreva "não foram necessários ajustes, mas identificamos outliers").
3. Retorne o resultado em formato JSON estrito, com uma única chave chamada "narrative" contendo o seu parágrafo.
   Exemplo: {{"narrative": "seu texto aqui"}}
4. Use um tom profissional, acessível, que prove o valor e o tempo que o usuário economizou.
"""


    import json
    raw_response, provider = call_ai_with_fallback(prompt)
    try:
        clean_json = raw_response.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        if clean_json.startswith("```"):
            clean_json = clean_json[3:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]
        clean_json = clean_json.strip()
        
        parsed = json.loads(clean_json)
        
        if isinstance(parsed, str):
            # As vezes a IA retorna um JSON string duplo
            parsed = json.loads(parsed)
            
        if "narrative" in parsed:
            final_text = parsed["narrative"]
        elif "resumo" in parsed:
            final_text = parsed["resumo"]
        else:
            final_text = list(parsed.values())[0] if parsed else raw_response
            
        return final_text, provider
    except Exception as e:
        print(f"Erro no parse do JSON: {e}, Raw: {raw_response}")
        # Se tudo falhar, tenta devolver o raw limpado
        return raw_response.replace('{"narrative":', '').replace('{"resumo":', '').replace('}', '').strip(' "'), provider
