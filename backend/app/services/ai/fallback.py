"""
Sistema de fallback entre provedores de IA (Etapa 5).

Ordem: Groq (mais rápido) → OpenRouter (gateway com ~30 modelos
gratuitos, tenta vários internamente) → NVIDIA NIM (empresa totalmente
diferente, contexto grande).

Cada provedor tem um TIMEOUT de 10 segundos: se não responder nesse
prazo, o sistema desiste imediatamente e passa ao próximo, em vez de
aguardar a resposta completa. O timeout é implementado via
concurrent.futures.ThreadPoolExecutor para não bloquear o event-loop.

Se um provedor falhar por qualquer motivo (timeout, erro de rede,
cota esgotada, chave inválida), o sistema tenta o próximo
automaticamente — o app só trava se os TRÊS falharem ao mesmo tempo.
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from .groq_client import call_groq_json
from .openrouter_client import call_openrouter_json
from .nvidia_nim_client import call_nvidia_json

logger = logging.getLogger(__name__)

# Ordem da cascata. Cada item: (nome_para_log, função_que_chama_a_api)
PROVIDERS = [
    ("groq", call_groq_json),
    ("openrouter", call_openrouter_json),
    ("nvidia_nim", call_nvidia_json),
]

# Tempo máximo de espera por provedor (segundos).
# Se o provedor não responder nesse prazo, desistimos e tentamos o próximo.
PROVIDER_TIMEOUT_SECONDS = 10


class AllProvidersFailedError(Exception):
    """Levantado só quando Groq, OpenRouter E NVIDIA NIM falharam."""

    def __init__(self, errors: dict[str, str]):
        self.errors = errors
        detail = "; ".join(f"{name}: {err}" for name, err in errors.items())
        super().__init__(f"Todos os provedores de IA falharam — {detail}")


def call_ai_with_fallback(prompt: str) -> tuple[str, str]:
    """
    Tenta cada provedor da cascata, na ordem, até um funcionar.

    Cada chamada tem um timeout de PROVIDER_TIMEOUT_SECONDS. Se o
    provedor não responder nesse prazo, o erro é registrado e o
    sistema avança imediatamente para o próximo provedor.

    Retorna:
        (resposta_em_texto, nome_do_provedor_que_respondeu)

    Levanta AllProvidersFailedError apenas se os três falharem.
    """
    errors: dict[str, str] = {}

    with ThreadPoolExecutor(max_workers=1) as executor:
        for name, call_fn in PROVIDERS:
            t0 = time.time()
            future = executor.submit(call_fn, prompt)
            try:
                logger.info("Tentando provedor de IA: %s (timeout=%ds)", name, PROVIDER_TIMEOUT_SECONDS)
                response = future.result(timeout=PROVIDER_TIMEOUT_SECONDS)
                duration = time.time() - t0
                logger.info("Sucesso com o provedor: %s (tempo: %.2fs)", name, duration)
                print(f"[FALLBACK_TIMING] Provedor {name} SUCESSO em {duration:.4f}s")
                return response, name
            except FuturesTimeoutError:
                duration = time.time() - t0
                msg = f"timeout após {duration:.1f}s (limite={PROVIDER_TIMEOUT_SECONDS}s)"
                logger.warning("Provedor %s: %s — tentando próximo", name, msg)
                print(f"[FALLBACK_TIMING] Provedor {name} TIMEOUT em {duration:.4f}s — avançando para o próximo")
                future.cancel()
                errors[name] = msg
            except Exception as e:
                duration = time.time() - t0
                logger.warning("Provedor %s falhou após %.2fs: %s", name, duration, e)
                print(f"[FALLBACK_TIMING] Provedor {name} FALHOU em {duration:.4f}s com erro: {e}")
                errors[name] = str(e)

    raise AllProvidersFailedError(errors)

