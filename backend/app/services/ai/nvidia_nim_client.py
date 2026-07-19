"""
Cliente de baixo nível para o NVIDIA NIM — novo fallback #3, substituindo
a Cerebras (que ficou travada com 402 Payment Required mesmo em conta
Personal nova).

Também compatível com o SDK da OpenAI. Empresa totalmente diferente da
Groq e do OpenRouter — importante pra reduzir a chance de dois elos da
cascata caírem pelo mesmo motivo (ex: uma instabilidade regional de um
único provedor de nuvem).
"""

import os
from openai import OpenAI

NVIDIA_MODEL = "meta/llama-3.1-70b-instruct"

_client: OpenAI | None = None


def get_nvidia_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("NVIDIA_API_KEY")
        if not api_key:
            raise RuntimeError("NVIDIA_API_KEY não encontrada no .env")
        _client = OpenAI(
            api_key=api_key, base_url="https://integrate.api.nvidia.com/v1"
        )
    return _client


def call_nvidia_json(prompt: str) -> str:
    """Chama o NVIDIA NIM pedindo resposta em JSON estrito."""
    client = get_nvidia_client()
    response = client.chat.completions.create(
        model=NVIDIA_MODEL,
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
    )
    return response.choices[0].message.content
