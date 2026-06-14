"""Flux Schnell provider — image generation via Together AI."""

import base64
import re

import httpx

from app.ai.base import (
    ImageProvider,
    ProviderAuthError,
    ProviderQuotaError,
    ProviderUnavailableError,
    ProviderError,
)
from app.core.config import settings


TOGETHER_BASE = "https://api.together.xyz"


class FluxImageProvider(ImageProvider):
    name = "flux"

    async def generate(
        self,
        prompt: str,
        **kwargs,
    ) -> tuple[bytes, str]:
        api_key = settings.together_api_key
        if not api_key:
            raise ProviderAuthError(self.name, "TOGETHER_API_KEY not configured")

        model = kwargs.get("model", settings.flux_model)
        width = kwargs.get("width", 1024)
        height = kwargs.get("height", 1024)

        body = {
            "model": f"black-forest-labs/{model}",
            "prompt": prompt,
            "width": width,
            "height": height,
            "steps": kwargs.get("steps", 4),
            "n": 1,
            "response_format": "b64_json",
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        url = f"{TOGETHER_BASE}/v1/images/generations"

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(url, headers=headers, json=body)

        if resp.status_code == 429:
            raise ProviderQuotaError(self.name, f"Together AI quota: {resp.text}")
        if resp.status_code == 401 or resp.status_code == 403:
            raise ProviderAuthError(self.name, f"Auth failed: {resp.text}")
        if resp.status_code >= 500:
            raise ProviderUnavailableError(
                self.name, f"Together AI error: {resp.text}"
            )
        if resp.status_code != 200:
            raise ProviderError(self.name, f"HTTP {resp.status_code}: {resp.text}")

        data = resp.json()
        try:
            b64 = data["data"][0]["b64_json"]
        except (KeyError, IndexError):
            raise ProviderError(
                self.name, f"Unexpected response structure: {data}"
            )

        return base64.b64decode(b64), "image/png"

    async def health(self) -> bool:
        try:
            return bool(settings.together_api_key)
        except Exception:
            return False
