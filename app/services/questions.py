"""Question generation for learning and review sessions.

Generates MCQ distractors, fill-in-the-blank, and FR→EN questions
using the database corpus — no AI dependency.
"""

import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expression import Expression


async def generate_mcq(
    expression: Expression,
    db: AsyncSession,
    count: int = 3,
) -> dict:
    """Generate an MCQ question with distractors from the same tier.

    Returns {"type":"MCQ","question":...,"options":[...],"hint":...}
    The correct answer is NOT included in the response — it is determined
    server-side during evaluation to prevent the client from seeing it.
    """
    # Fetch distractors: other expressions in the same tier, excluding this one
    tier_filter = expression.tier if expression.tier else 1
    stmt = (
        select(Expression)
        .where(
            Expression.id != expression.id,
            Expression.tier == tier_filter,
        )
        .order_by(Expression.difficulty)
        .limit(count * 3)  # over-fetch so we can shuffle and pick
    )
    result = await db.execute(stmt)
    candidates = list(result.scalars().all())
    random.shuffle(candidates)

    # Deduplicate distractors by meaning
    seen_meanings: set[str] = set()
    distractors: list[str] = []
    for c in candidates:
        if c.meaning not in seen_meanings:
            seen_meanings.add(c.meaning)
            distractors.append(c.meaning)
        if len(distractors) >= count:
            break

    # Pad if not enough distractors from same tier
    while len(distractors) < count:
        pad = f"(distractor {len(distractors) + 1})"
        if pad not in seen_meanings:
            seen_meanings.add(pad)
            distractors.append(pad)

    insert_pos = random.randint(0, count)
    options = distractors[:insert_pos] + [expression.meaning] + distractors[insert_pos:]
    options = options[: count + 1]

    hint = expression.metaphor or expression.example_sentence

    return {
        "type": "MCQ",
        "question": f"Que signifie l'expression « {expression.text} » ?",
        "expression_id": expression.id,
        "options": options,
        "hint": hint[:200] if hint else None,
    }


def generate_fill_blank(expression: Expression) -> dict:
    """Generate a fill-in-the-blank question.

    Shows the meaning, user must type the phrasal verb.
    """
    hint = expression.metaphor or expression.example_sentence
    return {
        "type": "FILL_BLANK",
        "expression_id": expression.id,
        "question": f"Quel phrasal verb signifie : « {expression.meaning} » ?",
        "correct": expression.text,
        "hint": hint[:200] if hint else None,
    }


def generate_fr_to_en(expression: Expression) -> dict:
    """Generate a French-to-English question.

    Uses the metaphor or context as a hint.
    """
    hint = expression.metaphor or expression.example_sentence
    return {
        "type": "FR_TO_EN",
        "expression_id": expression.id,
        "question": f"Comment dit-on en anglais l'idée de « {expression.meaning} » ?",
        "correct": expression.text,
        "hint": hint[:200] if hint else None,
    }


QUESTION_GENERATORS = {
    "MCQ": generate_mcq,
    "FILL_BLANK": generate_fill_blank,
    "FR_TO_EN": generate_fr_to_en,
}
