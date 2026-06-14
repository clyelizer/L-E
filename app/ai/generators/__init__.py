"""Expression card generators — turn corpus entries into rich flashcards via LLM."""

from app.ai.base import ProviderError
from app.ai.llm import LLMClient, AllProvidersFailed
from app.ai.schemas import GeneratedExpression, GenerateExpressionResponse
from app.ai.validators.expressions import validate_generated_card
from app.ai.prompts import load_prompt


async def generate_expression_card(
    expression: str,
    meaning: str,
    tier: int = 1,
    llm_client: LLMClient | None = None,
) -> GenerateExpressionResponse:
    """Generate a rich flashcard for a single phrasal verb expression.

    Returns a ``GenerateExpressionResponse`` regardless of success/failure.
    """
    client = llm_client or LLMClient()
    prompt = load_prompt("expression_prompt.txt").format(
        expression=expression, meaning=meaning, tier=tier
    )

    try:
        result = await client.generate(prompt, response_schema=GeneratedExpression)
    except AllProvidersFailed as e:
        return GenerateExpressionResponse(
            success=False,
            error=f"All LLM providers failed: {e}",
            provider_used="",
        )
    except ProviderError as e:
        return GenerateExpressionResponse(
            success=False,
            error=str(e),
            provider_used="",
        )

    if not isinstance(result, GeneratedExpression):
        return GenerateExpressionResponse(
            success=False,
            error=f"Unexpected response type: {type(result).__name__}",
            provider_used=client.providers[0].name if client.providers else "",
        )

    # Validate
    validation_error = validate_generated_card(result, expression)
    if validation_error:
        return GenerateExpressionResponse(
            success=False,
            generated=result,
            error=f"Validation failed: {validation_error}",
            provider_used=client.providers[0].name if client.providers else "",
        )

    return GenerateExpressionResponse(
        success=True,
        generated=result,
        provider_used=client.providers[0].name if client.providers else "",
    )


async def generate_expression_cards_batch(
    items: list[tuple[str, str, int]],
    llm_client: LLMClient | None = None,
) -> list[GenerateExpressionResponse]:
    """Generate flashcards for multiple expressions sequentially.

    Each item is a tuple of (expression, meaning, tier).
    """
    results: list[GenerateExpressionResponse] = []
    for expr, meaning, tier in items:
        resp = await generate_expression_card(expr, meaning, tier, llm_client)
        results.append(resp)
    return results
