"""
Resolução de grupos de texto ambíguos via IA (Etapa 4, atualizado na
Etapa 5 para fallback em cascata, e na Etapa 10 para o novo formato de
entrada: agora cada coluna manda TODOS os seus valores únicos, e é a
IA quem decide quantos grupos reais existem ali dentro e quais são a
mesma coisa — em vez de depender de pré-filtro por similaridade de
string, que não pega abreviações (ex: "SP" vs "São Paulo").

Ponto central que continua valendo: os candidatos de TODAS as colunas
são empacotados numa ÚNICA requisição, não uma requisição por coluna —
isso é o que minimiza o consumo de cota.
"""

import json

from .fallback import call_ai_with_fallback

# Limite de segurança pra decidir se precisa quebrar em mais de uma
# chamada. Bem folgado — colunas categóricas elegíveis já vêm filtradas
# por cardinalidade máxima em text_standardization.py.
MAX_VARIANTS_PER_REQUEST = 300


def _build_prompt(ambiguous_groups: dict) -> str:
    """
    Monta o prompt com TODOS os valores únicos de cada coluna
    categórica candidata. Diferente da versão anterior, aqui a IA
    recebe a lista inteira (não pré-agrupada) e precisa ELA MESMA
    identificar quais valores são a mesma informação escrita de forma
    diferente — abreviações incluídas (ex: "SP" = "São Paulo").
    """
    payload = {
        column: groups[0]["variants"]  # cada coluna chega como 1 lista única
        for column, groups in ambiguous_groups.items()
    }

    return f"""Você vai receber, por coluna de uma planilha, a lista de
TODOS os valores únicos que aparecem nela. Sua tarefa é encontrar quais
valores dessa lista representam a MESMA informação do mundo real,
escrita de formas diferentes — incluindo abreviações, siglas, erros de
digitação, variação de maiúscula/minúscula e acentuação.

Exemplos do tipo de agrupamento esperado (não são exaustivos):
- "SP", "S. Paulo", "sao paulo", "São Paulo" -> mesma cidade
- "RJ", "rio de janeiro", "Rio de Janeiro" -> mesma cidade
- "belem", "BELÉM", "Belém" -> mesma cidade

Regras:
- Só retorne grupos com 2 OU MAIS variantes que representem a mesma
  coisa. Se um valor da lista não tem nenhuma variação (já está
  sozinho, sem duplicata semântica), NÃO o inclua na resposta.
- Para cada grupo encontrado, decida o valor CANÔNICO: a forma
  correta e completa (prefira o nome por extenso e bem escrito em vez
  da abreviação, ex: "São Paulo" em vez de "SP")
- Nunca invente informação que não está nas variantes
- Uma coluna pode ter VÁRIOS grupos diferentes (ex: várias cidades
  distintas, cada uma com suas próprias variações)

Dados de entrada (todos os valores únicos, por coluna):
{json.dumps(payload, ensure_ascii=False, indent=2)}

Responda em JSON EXATAMENTE neste formato — uma lista de grupos por
coluna, só incluindo colunas/grupos onde encontrou algo pra unificar:
{{
  "nome_da_coluna": [
    {{"variants": ["SP", "São Paulo", "sao paulo"], "canonical": "São Paulo", "should_merge": true}}
  ]
}}
Se uma coluna não tiver nenhum grupo pra unificar, omita ela do JSON
de resposta (não retorne lista vazia).
"""


def resolve_ambiguous_groups(ambiguous_groups: dict) -> dict:
    """
    Recebe o `ambiguous_text_groups` que sai do cleaner.py (Etapa 3,
    formato atualizado na Etapa 10) e devolve as decisões da IA: quais
    grupos ela encontrou e qual o valor canônico de cada um.

    Retorna:
        {
          "decisions": {
            "cidade": [
              {"variants": ["SP", "São Paulo"], "canonical": "São Paulo", "should_merge": true}
            ]
          },
          "provider_used": "groq"
        }
    """
    if not ambiguous_groups:
        return {"decisions": {}, "provider_used": None}

    total_variants = sum(
        len(group["variants"])
        for groups in ambiguous_groups.values()
        for group in groups
    )

    if total_variants > MAX_VARIANTS_PER_REQUEST:
        # Fallback simples de volume: quebra por coluna quando o
        # texto é grande demais pra uma única chamada.
        decisions: dict = {}
        providers_used = set()
        for column, groups in ambiguous_groups.items():
            partial = resolve_ambiguous_groups({column: groups})
            decisions.update(partial["decisions"])
            if partial["provider_used"]:
                providers_used.add(partial["provider_used"])
        return {
            "decisions": decisions,
            "provider_used": ",".join(sorted(providers_used)) or None,
        }

    prompt = _build_prompt(ambiguous_groups)
    raw_response, provider_used = call_ai_with_fallback(prompt)

    # Limpa possíveis blocos markdown que alguns modelos retornam
    clean_response = raw_response.strip()
    if clean_response.startswith("```json"):
        clean_response = clean_response[7:]
    elif clean_response.startswith("```"):
        clean_response = clean_response[3:]
    if clean_response.endswith("```"):
        clean_response = clean_response[:-3]
    clean_response = clean_response.strip()

    try:
        decisions = json.loads(clean_response)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"{provider_used} devolveu um JSON inválido: {e}\n"
            f"Resposta bruta: {raw_response}"
        )

    return {"decisions": decisions, "provider_used": provider_used}
