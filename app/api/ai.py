"""AI generation routes — enrich expressions and generate images via provider chain."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.base import ProviderError
from app.ai.generators import generate_expression_card, generate_expression_cards_batch
from app.ai.generators.images import generate_expression_image
from app.ai.image import ImageClient
from app.ai.llm import LLMClient
from app.ai.schemas import (
    AIStatusResponse,
    BatchGenerateRequest,
    BatchGenerateResponse,
    BatchImageRequest,
    BatchImageResponse,
    GenerateExpressionRequest,
    GenerateExpressionResponse,
    GenerateImageRequest,
    GenerateImageResponse,
    GenerateImageResponse as SingleImageResponse,
    ProviderStatus,
)
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.config import settings
from app.models.expression import Expression, Image
from app.models.user import User

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])


@router.get("/status", response_model=AIStatusResponse)
async def ai_status(
    _current_user: User = Depends(get_current_user),
):
    """Check AI provider health."""
    if not settings.enable_ai:
        return AIStatusResponse(enabled=False, providers=[])

    providers: list[ProviderStatus] = []
    llm_client = LLMClient()
    for p in llm_client.providers:
        try:
            ok = await p.check_availability()
            providers.append(ProviderStatus(name=p.name, available=ok))
        except Exception as exc:
            providers.append(ProviderStatus(name=p.name, available=False, error=str(exc)))

    image_client = ImageClient()
    for p in image_client.providers:
        try:
            ok = await p.check_availability()
            providers.append(ProviderStatus(name=p.name, available=ok))
        except Exception as exc:
            providers.append(ProviderStatus(name=p.name, available=False, error=str(exc)))

    return AIStatusResponse(enabled=True, providers=providers)


@router.post("/generate", response_model=GenerateExpressionResponse)
async def generate_expression(
    body: GenerateExpressionRequest,
    _current_user: User = Depends(get_current_user),
):
    """Generate a rich flashcard for a single expression via LLM."""
    if not settings.enable_ai:
        raise HTTPException(status_code=503, detail="AI generation is disabled")
    return await generate_expression_card(body.expression, body.meaning, body.tier)


@router.post("/generate/batch", response_model=BatchGenerateResponse)
async def batch_generate_expressions(
    body: BatchGenerateRequest,
    _current_user: User = Depends(get_current_user),
):
    """Generate flashcards for multiple expressions."""
    if not settings.enable_ai:
        raise HTTPException(status_code=503, detail="AI generation is disabled")

    items = [(r.expression, r.meaning, r.tier) for r in body.items]
    results = await generate_expression_cards_batch(items)
    succeeded = sum(1 for r in results if r.success)

    return BatchGenerateResponse(
        success=succeeded == len(results),
        total=len(results),
        succeeded=succeeded,
        failed=len(results) - succeeded,
        results=results,
    )


@router.post("/image", response_model=GenerateImageResponse)
async def generate_image(
    body: GenerateImageRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Generate an image for an expression using its metaphor."""
    if not settings.enable_ai:
        raise HTTPException(status_code=503, detail="AI generation is disabled")
    return await generate_expression_image(body.expression_id, db)


@router.post("/image/batch", response_model=BatchImageResponse)
async def batch_generate_images(
    body: BatchImageRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Generate images for multiple expressions."""
    if not settings.enable_ai:
        raise HTTPException(status_code=503, detail="AI generation is disabled")

    results: list[GenerateImageResponse] = []
    for eid in body.expression_ids:
        resp = await generate_expression_image(eid, db)
        results.append(resp)

    succeeded = sum(1 for r in results if r.success)
    return BatchImageResponse(
        success=succeeded == len(results),
        total=len(results),
        succeeded=succeeded,
        failed=len(results) - succeeded,
        results=results,
    )


@router.post("/enrich/missing", response_model=BatchGenerateResponse)
async def enrich_missing_expressions(
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Enrich all expressions that lack a metaphor (batch admin endpoint)."""
    if not settings.enable_ai:
        raise HTTPException(status_code=503, detail="AI generation is disabled")

    result = await db.execute(
        select(Expression).where(Expression.metaphor.is_(None))
    )
    missing = result.scalars().all()

    if not missing:
        return BatchGenerateResponse(
            success=True, total=0, succeeded=0, failed=0, results=[]
        )

    items = [(e.text, e.meaning, e.tier) for e in missing]
    results = await generate_expression_cards_batch(items)

    # Persist successful enrichments
    succeeded_responses = [r for r in results if r.success and r.generated]
    for resp, expr in zip(succeeded_responses, missing):
        gen = resp.generated
        expr.metaphor = gen.metaphor
        expr.example_sentence = gen.examples[0] if gen.examples else ""
        expr.difficulty = gen.difficulty
        expr.frequency_score = gen.frequency_score
        expr.tags = gen.tags

    await db.flush()

    succeeded = sum(1 for r in results if r.success)
    return BatchGenerateResponse(
        success=succeeded == len(results),
        total=len(results),
        succeeded=succeeded,
        failed=len(results) - succeeded,
        results=results,
    )


@router.post("/images/missing", response_model=BatchImageResponse)
async def generate_missing_images(
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Generate images for all expressions that lack one (batch admin endpoint)."""
    if not settings.enable_ai:
        raise HTTPException(status_code=503, detail="AI generation is disabled")

    # Expressions that have a metaphor but no active image
    result = await db.execute(
        select(Expression).where(
            Expression.metaphor.isnot(None),
            ~Expression.images.any(Image.is_active.is_(True)),
        )
    )
    missing = result.unique().scalars().all()

    if not missing:
        return BatchImageResponse(
            success=True, total=0, succeeded=0, failed=0, results=[]
        )

    results: list[GenerateImageResponse] = []
    for expr in missing:
        resp = await generate_expression_image(str(expr.id), db)
        results.append(resp)

    succeeded = sum(1 for r in results if r.success)
    return BatchImageResponse(
        success=succeeded == len(results),
        total=len(results),
        succeeded=succeeded,
        failed=len(results) - succeeded,
        results=results,
    )
