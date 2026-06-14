"""Unified LLM client with provider fallback chain."""

from app.ai.base import (
    LLMProvider,
    ProviderError,
    ProviderQuotaError,
    ProviderAuthError,
    ProviderUnavailableError,
)
from app.ai.providers.deepseek import DeepSeekLLMProvider
from app.ai.providers.gemini import GeminiLLMProvider
from app.core.config import settings


_PROVIDER_MAP: dict[str, type[LLMProvider]] = {
    "deepseek": DeepSeekLLMProvider,
    "gemini": GeminiLLMProvider,
}


def _build_providers() -> list[LLMProvider]:
    chain = settings.llm_provider_list
    if not chain:
        raise ValueError(
            "No LLM providers configured. Set LLM_PROVIDERS in .env "
            "(e.g. 'deepseek,gemini')"
        )
    providers: list[LLMProvider] = []
    for name in chain:
        cls = _PROVIDER_MAP.get(name)
        if cls is None:
            raise ValueError(f"Unknown LLM provider: {name} (options: {list(_PROVIDER_MAP)})")
        providers.append(cls())
    return providers


class LLMClient:
    """Unified LLM client with automatic fallback across providers.

    The provider chain is defined by ``LLM_PROVIDERS`` in .env.
    On quota or auth errors the client falls through to the next
    provider.  Other errors (network, unexpected response) also
    trigger fallback so the call rarely fails outright.
    """

    def __init__(self, providers: list[LLMProvider] | None = None):
        self.providers = providers or _build_providers()
        if not self.providers:
            raise ValueError("At least one LLM provider is required.")

    async def generate(self, prompt: str, response_schema=None, **kwargs):
        """Generate text, falling back through the provider chain.

        Raises ``AllProvidersFailed`` if every provider fails.
        """
        errors: list[str] = []
        for provider in self.providers:
            try:
                return await provider.generate(prompt, response_schema, **kwargs)
            except ProviderQuotaError as e:
                errors.append(f"{provider.name}: quota ({e})")
                continue
            except ProviderAuthError as e:
                errors.append(f"{provider.name}: auth ({e})")
                continue
            except ProviderUnavailableError as e:
                errors.append(f"{provider.name}: unavailable ({e})")
                continue
            except ProviderError as e:
                errors.append(f"{provider.name}: error ({e})")
                continue

        raise AllProvidersFailed(errors)

    async def health(self) -> list[tuple[str, bool]]:
        results: list[tuple[str, bool]] = []
        for provider in self.providers:
            try:
                ok = await provider.health()
            except Exception:
                ok = False
            results.append((provider.name, ok))
        return results


class AllProvidersFailed(Exception):
    """All LLM providers in the chain failed."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        details = "; ".join(errors)
        super().__init__(f"All LLM providers failed: {details}")
