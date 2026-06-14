"""Gemini provider — text generation + image generation via Google AI Studio API."""

import base64
import re

import httpx
from pydantic import BaseModel

from app.ai.base import (
    LLMProvider,
    ImageProvider,
    ProviderAuthError,
    ProviderQuotaError,
    ProviderUnavailableError,
    ProviderError,
)
from app.core.config import settings


GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"


def _headers() -> dict:
    api_key = settings.gemini_api_key
    if not api_key:
        raise ProviderAuthError("gemini", "GEMINI_API_KEY not configured")
    return {"Content-Type": "application/json"}


def _url(model: str, action: str = "generateContent") -> str:
    key = settings.gemini_api_key
    return f"{GEMINI_BASE}/models/{model}:{action}?key={key}"


def _check_response(resp: httpx.Response, provider_name: str) -> dict:
    if resp.status_code == 429:
        raise ProviderQuotaError(provider_name, f"Quota exceeded: {resp.text}")
    if resp.status_code in (401, 403):
        raise ProviderAuthError(provider_name, f"Auth failed: {resp.text}")
    if resp.status_code >= 500:
        raise ProviderUnavailableError(provider_name, f"Server error: {resp.text}")
    if resp.status_code != 200:
        raise ProviderError(provider_name, f"HTTP {resp.status_code}: {resp.text}")
    return resp.json()


# ── Helpers ─────────────────────────────────────────────────────

def _pydantic_to_gemini_schema(model: type[BaseModel]) -> dict:
    """Convert Pydantic model schema to Gemini responseSchema format."""
    schema = model.model_json_schema()

    def walk(s: dict) -> dict:
        result: dict = {}
        t = s.get("type", "")
        if t == "object":
            result["type"] = "OBJECT"
            required = set(s.get("required", []))
            props = {}
            for pname, pval in s.get("properties", {}).items():
                props[pname] = walk(pval)
                if pname in required and pval.get("default", None) is None:
                    props[pname].setdefault("nullable", False)
            result["properties"] = props
            result["required"] = list(required)
        elif t == "array":
            result["type"] = "ARRAY"
            result["items"] = walk(s.get("items", {}))
        elif t == "string":
            result["type"] = "STRING"
        elif t in ("number", "integer"):
            result["type"] = "INTEGER" if t == "integer" else "NUMBER"
        elif t == "boolean":
            result["type"] = "BOOLEAN"
        else:
            result["type"] = "STRING"
        if "description" in s:
            result["description"] = s["description"]
        return result

    return walk(schema)


def _strip_markdown_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("\n", 1)[0]
        cleaned = cleaned.strip()
    return cleaned


# ── LLM Provider ────────────────────────────────────────────────

class GeminiLLMProvider(LLMProvider):
    name = "gemini"

    async def generate(
        self,
        prompt: str,
        response_schema: type[BaseModel] | None = None,
        **kwargs,
    ) -> str | BaseModel:
        model = settings.gemini_llm_model
        body: dict = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": kwargs.get("max_tokens", settings.llm_max_tokens),
                "temperature": kwargs.get("temperature", settings.llm_temperature),
            },
        }

        if response_schema is not None:
            body["generationConfig"]["responseMimeType"] = "application/json"
            body["generationConfig"]["responseSchema"] = _pydantic_to_gemini_schema(
                response_schema
            )

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(_url(model), headers=_headers(), json=body)

        data = _check_response(resp, self.name)

        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            raise ProviderError(self.name, f"Unexpected response: {data}")

        if response_schema is not None:
            cleaned = _strip_markdown_fences(text)
            return response_schema.model_validate_json(cleaned)

        return text

    async def health(self) -> bool:
        try:
            await self.generate("Say OK", max_tokens=5)
            return True
        except Exception:
            return False


# ── Image Provider ──────────────────────────────────────────────

class GeminiImageProvider(ImageProvider):
    name = "gemini_image"

    async def generate(
        self,
        prompt: str,
        **kwargs,
    ) -> tuple[bytes, str]:
        model = settings.gemini_image_model
        body: dict = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": kwargs.get("temperature", 0.4),
                "maxOutputTokens": kwargs.get("max_tokens", 4096),
            },
        }

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(_url(model), headers=_headers(), json=body)

        data = _check_response(resp, self.name)

        try:
            parts = data["candidates"][0]["content"]["parts"]
        except (KeyError, IndexError):
            raise ProviderError(self.name, f"No candidates: {data}")

        # Direct inline image data
        for part in parts:
            if "inlineData" in part:
                b64_data = part["inlineData"]["data"]
                mime = part["inlineData"]["mimeType"]
                return base64.b64decode(b64_data), mime

        # Fallback: data URL embedded in text
        for part in parts:
            text = part.get("text", "")
            match = re.search(r"data:image/(\w+);base64,([^\"'\s]+)", text)
            if match:
                return base64.b64decode(match.group(2)), f"image/{match.group(1)}"

        raise ProviderError(
            self.name,
            "No image data found in Gemini response. "
            "The model may not support inline image output.",
        )

    async def health(self) -> bool:
        return bool(settings.gemini_api_key)
