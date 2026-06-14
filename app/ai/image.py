"""Unified Image client with provider fallback chain."""

from app.ai.base import (
    ImageProvider,
    ProviderError,
    ProviderQuotaError,
    ProviderAuthError,
    ProviderUnavailableError,
)
from app.ai.providers.gemini import GeminiImageProvider
from app.ai.providers.flux import FluxImageProvider
from app.core.config import settings


_PROVIDER_MAP: dict[str, type[ImageProvider]] = {
    "gemini": GeminiImageProvider,
    "flux": FluxImageProvider,
}


def _build_providers() -> list[ImageProvider]:
    chain = settings.image_provider_list
    if not chain:
        raise ValueError(
            "No image providers configured. Set IMAGE_PROVIDERS in .env "
            "(e.g. 'gemini,flux')"
        )
    providers: list[ImageProvider] = []
    for name in chain:
        cls = _PROVIDER_MAP.get(name)
        if cls is None:
            raise ValueError(
                f"Unknown image provider: {name} (options: {list(_PROVIDER_MAP)})"
            )
        providers.append(cls())
    return providers


class ImageClient:
    """Unified image client with automatic fallback across providers.

    The provider chain is defined by ``IMAGE_PROVIDERS`` in .env.
    """

    def __init__(self, providers: list[ImageProvider] | None = None):
        self.providers = providers or _build_providers()
        if not self.providers:
            raise ValueError("At least one image provider is required.")

    async def generate(
        self, prompt: str, **kwargs
    ) -> tuple[bytes, str, str]:
        """Generate image, returns (bytes, mime_type, provider_name).

        Falls back through the provider chain on failure.
        """
        errors: list[str] = []
        for provider in self.providers:
            try:
                data, mime = await provider.generate(prompt, **kwargs)
                return data, mime, provider.name
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

        raise AllImageProvidersFailed(errors)

    async def health(self) -> list[tuple[str, bool]]:
        results: list[tuple[str, bool]] = []
        for provider in self.providers:
            try:
                ok = await provider.health()
            except Exception:
                ok = False
            results.append((provider.name, ok))
        return results


class AllImageProvidersFailed(Exception):
    """All image providers in the chain failed."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        details = "; ".join(errors)
        super().__init__(f"All image providers failed: {details}")
