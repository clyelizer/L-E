#!/usr/bin/env python3
"""Batch enrichment: generate metaphors/examples for expressions that lack them."""

import asyncio
import sys
from pathlib import Path

# Ensure app is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.generators import generate_expression_card
from app.ai.schemas import GenerateExpressionResponse
from app.core.database import async_session_factory
from app.models.expression import Expression

# Import models so SQLAlchemy can resolve relationships
import app.models.user  # noqa: F401
import app.models.memory  # noqa: F401
import app.models.session  # noqa: F401
import app.models.mistake  # noqa: F401


async def enrich():
    async with async_session_factory() as db:
        result = await db.execute(
            select(Expression).where(Expression.metaphor.is_(None))
        )
        missing = list(result.scalars().all())

        if not missing:
            print("All expressions already have a metaphor. Nothing to do.")
            return

        total = len(missing)
        succeeded = 0
        failed = 0

        print(f"Found {total} expression(s) without metaphor — enriching...\n")

        for expr in missing:
            resp: GenerateExpressionResponse = await generate_expression_card(
                expr.text, expr.meaning, expr.tier
            )

            if resp.success and resp.generated:
                gen = resp.generated
                expr.metaphor = gen.metaphor
                expr.example_sentence = gen.examples[0] if gen.examples else ""
                expr.difficulty = gen.difficulty
                expr.frequency_score = gen.frequency_score
                expr.tags = gen.tags
                succeeded += 1
                print(f"  ✅ [{succeeded}/{total}] {expr.text}")
            else:
                failed += 1
                print(f"  ❌ [{succeeded + failed}/{total}] {expr.text} — {resp.error}")

        await db.flush()
        await db.commit()

    print(f"\nDone. {succeeded} enriched, {failed} failed.")


if __name__ == "__main__":
    asyncio.run(enrich())
