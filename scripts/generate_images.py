#!/usr/bin/env python3
"""Batch image generation: generate images for expressions that lack one."""

import asyncio
import sys
from pathlib import Path

# Ensure app is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.ai.generators.images import generate_expression_image
from app.ai.schemas import GenerateImageResponse
from app.core.database import async_session_factory
from app.models.expression import Expression, Image

# Import models so SQLAlchemy can resolve relationships
import app.models.user  # noqa: F401
import app.models.memory  # noqa: F401
import app.models.session  # noqa: F401
import app.models.mistake  # noqa: F401


async def generate():
    async with async_session_factory() as db:
        # Expressions that have a metaphor but no active image
        result = await db.execute(
            select(Expression)
            .options(joinedload(Expression.images))
            .where(
                Expression.metaphor.isnot(None),
                ~Expression.images.any(Image.is_active.is_(True)),
            )
        )
        missing = list(result.unique().scalars().all())

        if not missing:
            print("All expressions with a metaphor already have an image. Nothing to do.")
            return

        total = len(missing)
        succeeded = 0
        failed = 0

        print(f"Found {total} expression(s) without image — generating...\n")

        for expr in missing:
            resp: GenerateImageResponse = await generate_expression_image(
                str(expr.id), db
            )

            if resp.success:
                succeeded += 1
                print(f"  ✅ [{succeeded}/{total}] {expr.text} → {resp.provider_used}")
            else:
                failed += 1
                print(f"  ❌ [{succeeded + failed}/{total}] {expr.text} — {resp.error}")

        await db.commit()

    print(f"\nDone. {succeeded} images generated, {failed} failed.")


if __name__ == "__main__":
    asyncio.run(generate())
