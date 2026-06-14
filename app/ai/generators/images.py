"""Image generators — turn expression metaphors into images via image API."""

import hashlib
from pathlib import Path
from slugify import slugify

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.base import ProviderError
from app.ai.image import ImageClient, AllImageProvidersFailed
from app.ai.prompts import load_prompt
from app.ai.schemas import GenerateImageResponse
from app.ai.validators.images import validate_image_bytes
from app.core.config import settings
from app.models.expression import Expression, Image


async def generate_expression_image(
    expression_id: str,
    db: AsyncSession,
    image_client: ImageClient | None = None,
) -> GenerateImageResponse:
    """Generate an image for an expression using its metaphor.

    Fetches the expression from DB, builds the prompt, calls the
    image API, saves the file, and persists the Image record.
    """
    client = image_client or ImageClient()

    # Fetch expression
    result = await db.execute(
        select(Expression).where(Expression.id == expression_id)
    )
    expression = result.scalar_one_or_none()
    if not expression:
        return GenerateImageResponse(
            success=False,
            error=f"Expression not found: {expression_id}",
        )

    metaphor = expression.metaphor
    if not metaphor:
        return GenerateImageResponse(
            success=False,
            expression_text=expression.text,
            error="Expression has no metaphor — cannot generate image without one",
        )

    # Build prompt
    prompt = load_prompt("image_prompt.txt").format(
        expression=expression.text,
        meaning_fr=expression.meaning,
        metaphor=metaphor,
    )

    # Generate image
    try:
        image_bytes, mime_type, provider_name = await client.generate(prompt)
    except AllImageProvidersFailed as e:
        return GenerateImageResponse(
            success=False,
            expression_text=expression.text,
            error=f"All image providers failed: {e}",
        )
    except ProviderError as e:
        return GenerateImageResponse(
            success=False,
            expression_text=expression.text,
            error=str(e),
        )

    # Validate image
    validation = validate_image_bytes(image_bytes)
    if validation:
        return GenerateImageResponse(
            success=False,
            expression_text=expression.text,
            error=f"Image validation failed: {validation}",
            provider_used=provider_name,
        )

    # Determine next version
    existing = await db.execute(
        select(Image)
        .where(Image.expression_id == expression_id, Image.is_active.is_(True))
        .order_by(Image.version.desc())
        .limit(1)
    )
    latest = existing.scalar_one_or_none()
    next_version = (latest.version + 1) if latest else 1

    # Save file
    ext = _mime_to_ext(mime_type)
    filename = f"{slugify(expression.text)}_{next_version}.{ext}"
    image_dir = settings.image_dir
    image_dir.mkdir(parents=True, exist_ok=True)
    filepath = image_dir / filename
    filepath.write_bytes(image_bytes)

    # Compute hash
    sha256 = hashlib.sha256(image_bytes).hexdigest()

    # Persist DB record
    image_record = Image(
        expression_id=expression_id,
        path=str(filepath),
        prompt_used=prompt,
        version=next_version,
        width=None,
        height=None,
        file_size_bytes=len(image_bytes),
        hash_sha256=sha256,
        is_active=True,
    )
    db.add(image_record)
    await db.flush()

    # Deactivate older versions
    if latest:
        latest.is_active = False

    return GenerateImageResponse(
        success=True,
        image_id=image_record.id,
        path=str(filepath),
        expression_text=expression.text,
        provider_used=provider_name,
    )


def _mime_to_ext(mime: str) -> str:
    mapping = {
        "image/png": "png",
        "image/jpeg": "jpg",
        "image/jpg": "jpg",
        "image/webp": "webp",
    }
    return mapping.get(mime, "png")
