"""Abstract base classes for LLM and Image providers."""

from abc import ABC, abstractmethod
from pydantic import BaseModel


# ── Custom exceptions ───────────────────────────────────────────

class ProviderError(Exception):
    """Base error for all AI provider failures."""
    def __init__(self, provider: str, message: str, original: Exception | None = None):
        self.provider = provider
        self.original = original
        super().__init__(f"[{provider}] {message}")


class ProviderQuotaError(ProviderError):
    """Raised when provider returns 429 / quota exceeded."""
    pass


class ProviderAuthError(ProviderError):
    """Raised on 401 / invalid API key."""
    pass


class ProviderUnavailableError(ProviderError):
    """Raised on network failure or 5xx."""
    pass


# ── Abstract providers ──────────────────────────────────────────

class LLMProvider(ABC):
    """Abstract LLM provider for text generation."""

    name: str

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        response_schema: type[BaseModel] | None = None,
        **kwargs,
    ) -> str | BaseModel:
        """Generate text, optionally constrained to a Pydantic schema."""
        ...

    @abstractmethod
    async def health(self) -> bool:
        """Check if the provider is reachable and configured."""
        ...


class ImageProvider(ABC):
    """Abstract image provider."""

    name: str

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        **kwargs,
    ) -> tuple[bytes, str]:
        """Generate image, returns (image_bytes, mime_type)."""
        ...

    @abstractmethod
    async def health(self) -> bool:
        """Check if the provider is reachable and configured."""
        ...
