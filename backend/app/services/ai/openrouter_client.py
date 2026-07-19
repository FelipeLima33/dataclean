"""
Cliente de baixo nível para o OpenRouter — fallback #2 da cascata.

Ponto importante sobre qualidade: em vez de deixar o roteador
totalmente automático ("openrouter/free") escolher qualquer modelo
disponível — o que pode variar de qualidade entre chamadas — usamos o
recurso NATIVO de fallback do OpenRouter: uma lista de modelos em
ORDEM DE PRIORIDADE, passada numa única requisição. O OpenRouter tenta
o primeiro (melhor qualidade); só desce pro próximo se o anterior
falhar de verdade (indisponível, sobrecarregado, saiu do tier grátis).
"openrouter/free" fica só como ÚLTIMO recurso da lista, não como
padrão — assim a qualidade fica previsível na maioria das vezes, e a
resiliência continua garantida.

Atualize esta lista periodicamente — o roster de modelos gratuitos do
OpenRouter muda com frequência. Confira o catálogo atual em
https://openrouter.ai/models?max_price=0
"""

import os
from openai import OpenAI

# Modelo principal — o de melhor qualidade/estabilidade no momento.
PRIMARY_MODEL = "deepseek/deepseek-chat-v3.1:free"

# Ordem de prioridade dos fallbacks, do melhor pro mais genérico.
# O OpenRouter só desce a lista se o anterior falhar de verdade.
FALLBACK_MODELS = [
    "meta-llama/llama-4-maverick:free",
    "google/gemini-2.0-flash-exp:free",
    "openrouter/free",  # último recurso: deixa o roteador escolher
]

_client: OpenAI | None = None


def get_openrouter_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY não encontrada no .env")
        _client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
    return _client


def call_openrouter_json(prompt: str) -> str:
    """
    Chama o OpenRouter com fallback nativo entre modelos, numa única
    requisição. O modelo que efetivamente respondeu vem no campo
    `model` da resposta, útil pra log/observabilidade.
    """
    client = get_openrouter_client()

    response = client.chat.completions.create(
        model=PRIMARY_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Você responde APENAS com JSON válido, sem nenhum "
                    "texto antes ou depois, sem markdown."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0,
        extra_headers={"X-Title": "DataClean"},
        extra_body={"models": FALLBACK_MODELS},
    )

    return response.choices[0].message.content
