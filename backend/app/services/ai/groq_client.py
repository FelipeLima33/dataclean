"""
Cliente de baixo nível para a API do Groq.

Nesta etapa só implementamos a chamada isolada ao Groq. O sistema de
fallback (tentar Gemini/Cerebras se o Groq falhar ou esgotar cota) fica
pra Etapa 5 — aqui é só validar que a conexão funciona.

Nota sobre o modelo: o Groq descontinua/atualiza modelos com frequência.
Estamos usando "openai/gpt-oss-120b" (bom equilíbrio custo/qualidade no
tier gratuito, em vigor em julho/2026). Se a chamada começar a falhar
com erro de "model not found", confira o modelo atual em
https://console.groq.com/docs/models e atualize a constante abaixo.
"""

import os
from groq import Groq

GROQ_MODEL = "openai/gpt-oss-120b"

_client: Groq | None = None


def get_groq_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY não encontrada no .env. "
                "Pegue sua chave grátis em console.groq.com"
            )
        _client = Groq(api_key=api_key)
    return _client


def call_groq_json(prompt: str) -> str:
    """
    Chama o Groq pedindo resposta em JSON estrito e devolve o texto
    bruto da resposta (ainda não parseado).
    """
    client = get_groq_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Você responde APENAS com JSON válido, sem nenhum "
                    "texto antes ou depois, sem markdown, sem ```."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content
