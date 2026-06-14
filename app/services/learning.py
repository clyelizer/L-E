"""Learning service — introduces new expressions to the user."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.engines.sm2 import quality_from_correct, sm2_calculate
from app.models.expression import Expression
from app.models.memory import UserMemory
from app.models.session import SessionAnswer, StudySession
from app.models.user import User, UserSettings


async def get_daily_new_word_count(user_id: str, db: AsyncSession) -> int:
    """Return how many new words the user has learned today."""
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    stmt = select(func.count(UserMemory.id)).where(
        UserMemory.user_id == user_id,
        UserMemory.first_seen_at >= today_start,
    )
    result = await db.execute(stmt)
    return result.scalar() or 0


async def pick_new_expressions(
    user_id: str,
    word_count: int,
    db: AsyncSession,
) -> list[Expression]:
    """Pick expressions not yet seen by this user, ordered by tier then random."""
    # Subquery: expression_ids already in user_memory for this user
    seen_subq = select(UserMemory.expression_id).where(UserMemory.user_id == user_id).subquery()

    stmt = (
        select(Expression)
        .where(Expression.id.notin_(select(seen_subq)))
        .order_by(Expression.tier.asc().nullsfirst(), func.random())
        .limit(word_count)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def start_learning(
    user_id: str,
    word_count: int,
    db: AsyncSession,
) -> tuple[StudySession, list[dict]]:
    """Start a learning session: pick new words, create memory + session records."""
    expressions = await pick_new_expressions(user_id, word_count, db)

    if not expressions:
        raise ValueError("Aucun nouveau mot disponible. Tu as peut-être tout vu !")

    # Create StudySession
    session = StudySession(
        user_id=user_id,
        session_type="learn",
        total_questions=len(expressions),
    )
    db.add(session)
    await db.flush()

    # Create UserMemory for each expression (is_learning=True)
    now = datetime.now(timezone.utc)
    cards = []
    for expr in expressions:
        memory = UserMemory(
            user_id=user_id,
            expression_id=expr.id,
            is_learning=True,
            next_review_at=now,  # due immediately for first review
        )
        db.add(memory)
        cards.append({
            "expression_id": expr.id,
            "text": expr.text,
            "meaning": expr.meaning,
            "metaphor": expr.metaphor,
            "example_sentence": expr.example_sentence,
            "image_path": None,  # Phase 3 will populate this
        })

    await db.flush()
    return session, cards


async def submit_learning_answer(
    session_id: str,
    expression_id: str,
    user_id: str,
    user_answer: str,
    response_time_ms: int | None,
    db: AsyncSession,
) -> dict:
    """Evaluate a learning answer, run SM-2, record the result."""
    # Verify session belongs to this user
    sess_result = await db.execute(
        select(StudySession).where(
            StudySession.id == session_id,
            StudySession.user_id == user_id,
        )
    )
    if not sess_result.scalar_one_or_none():
        raise ValueError("Session introuvable")

    # Fetch expression + current memory
    expr_result = await db.execute(select(Expression).where(Expression.id == expression_id))
    expression = expr_result.scalar_one_or_none()
    if not expression:
        raise ValueError("Expression introuvable")

    mem_result = await db.execute(
        select(UserMemory).where(
            UserMemory.user_id == user_id,
            UserMemory.expression_id == expression_id,
        )
    )
    memory = mem_result.scalar_one_or_none()
    if not memory:
        raise ValueError("Aucune mémoire trouvée pour cette expression")

    # Determine correctness — compare answer to meaning (case-insensitive, strip)
    is_correct = user_answer.strip().lower() == expression.meaning.strip().lower()
    quality = quality_from_correct(is_correct, response_time_ms)

    # Run SM-2
    result = sm2_calculate(
        quality=quality,
        repetitions=memory.repetitions,
        ease_factor=memory.ease_factor,
        interval=memory.interval,
    )

    # Update UserMemory
    now = datetime.now(timezone.utc)
    memory.mastery_score = result.mastery_score
    memory.interval = result.interval
    memory.ease_factor = result.ease_factor
    memory.repetitions = result.repetitions
    memory.total_reviews += 1
    memory.last_reviewed_at = now
    memory.next_review_at = now  # review immediately again (is_learning)
    memory.is_learning = not is_correct  # keep learning until correct
    if is_correct:
        memory.correct_count += 1
        # After first correct answer, move to review queue
        memory.next_review_at = now + timedelta(hours=1)
    else:
        memory.incorrect_count += 1
        memory.lapses += 1
        memory.next_review_at = now + timedelta(minutes=5)  # quick retry

    # Record SessionAnswer
    answer = SessionAnswer(
        session_id=session_id,
        expression_id=expression_id,
        user_id=user_id,
        question_type="LEARN",
        question_data={"type": "direct_recall"},
        user_answer=user_answer,
        correct_answer=expression.meaning,
        is_correct=is_correct,
        response_time_ms=response_time_ms,
    )
    db.add(answer)
    await db.flush()

    return {
        "is_correct": is_correct,
        "quality": quality,
        "correct_answer": expression.meaning,
        "mastery_score": result.mastery_score,
        "next_review_at": memory.next_review_at.isoformat() if memory.next_review_at else None,
    }


async def complete_learning(session_id: str, user_id: str, db: AsyncSession) -> dict:
    """Finalize a learning session."""
    result = await db.execute(
        select(StudySession).where(
            StudySession.id == session_id,
            StudySession.user_id == user_id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise ValueError("Session introuvable")

    # Count correct answers
    answers_result = await db.execute(
        select(func.count(SessionAnswer.id)).where(
            SessionAnswer.session_id == session_id,
            SessionAnswer.is_correct == True,
        )
    )
    correct_count = answers_result.scalar() or 0

    # Calculate stats
    now = datetime.now(timezone.utc)
    duration = int((now - session.started_at).total_seconds())
    score = round(correct_count / max(session.total_questions, 1) * 100, 1)

    session.status = "completed"
    session.correct_answers = correct_count
    session.score = score
    session.duration_seconds = duration
    session.completed_at = now
    await db.flush()

    return {
        "session_id": session_id,
        "words_learned": session.total_questions,
        "score": score,
        "avg_response_time_ms": None,
    }
