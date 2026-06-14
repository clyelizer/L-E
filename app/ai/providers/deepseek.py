"""DeepSeek provider — text generation via DeepSeek API."""

import json

import httpx
from pydantic import BaseModel

from app.ai.base import (
    LLMProvider,
    ProviderAuthError,
    ProviderQuotaError,
    ProviderUnavailableError,
    ProviderError,
)
from app.core.config import settings


class DeepSeekLLMProvider(LLMProvider):
    name = "deepseek"

    async def generate(
        self,
        prompt: str,
        response_schema: type[BaseModel] | None = None,
        **kwargs,
    ) -> str | BaseModel:
        api_key = settings.deepseek_api_key
        if not api_key:
            raise ProviderAuthError(self.name, "DEEPSEEK_API_KEY not configured")

        base = kwargs.get("api_base", settings.deepseek_api_base)
        model = kwargs.get("model", settings.deepseek_model)

        messages = [{"role": "user", "content": prompt}]
        body: dict = {
            "model": model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", settings.llm_max_tokens),
            "temperature": kwargs.get("temperature", settings.llm_temperature),
        }

        if response_schema is not None:
            schema_json = response_schema.model_json_schema()
            body["response_format"] = {
                "type": "json_object",
                "schema": schema_json,
            }
            # Instruct the model to output valid JSON matching the schema
            schema_desc = json.dumps(schema_json, indent=2)
            prompt_with_schema = (
                f"{prompt}\n\n"
                f"Respond ONLY with valid JSON matching this schema:\n"
                f"```json\n{schema_desc}\n```"
            )
            body["messages"][0]["content"] = prompt_with_schema

        url = f"{base.rstrip('/')}/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, headers=headers, json=body)

        if resp.status_code == 429:
            raise ProviderQuotaError(self.name, f"Quota exceeded: {resp.text}")
        if resp.status_code == 401 or resp.status_code == 403:
            raise ProviderAuthError(self.name, f"Auth failed: {resp.text}")
        if resp.status_code >= 500:
            raise ProviderUnavailableError(self.name, f"Server error: {resp.text}")
        if resp.status_code != 200:
            raise ProviderError(self.name, f"HTTP {resp.status_code}: {resp.text}")

        data = resp.json()
        try:
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            raise ProviderError(self.name, f"Unexpected response: {data}")

        if response_schema is not None:
            cleaned = text.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[-1]
                cleaned = cleaned.rsplit("\n", 1)[0] if cleaned.endswith("```") else cleaned
                cleaned = cleaned.strip()
            return response_schema.model_validate_json(cleaned)

        return text

    async def health(self) -> bool:
        try:
            _ = await self.generate("Say OK", max_tokens=5)
            return True
        except Exception:
            return False
