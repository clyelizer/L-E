"""
learnEnglish — AI pipeline
===========================
Multimodal content generation with provider fallback.

Providers
---------
- LLM: DeepSeek (primary) -> Gemini (fallback)
- Image: Gemini (primary) -> Flux Schnell via Together AI (fallback)

Architecture
------------
schemas.py       -> Pydantic I/O models
base.py          -> Abstract provider interfaces
llm.py           -> Unified LLM client with fallback chain
image.py         -> Unified image client with fallback chain
providers/       -> Concrete provider implementations
generators/      -> Expression card + image generation logic
validators/      -> Post-generation validation (structure, quality)
prompts/         -> Prompt templates
"""
