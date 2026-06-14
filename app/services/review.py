"""Review service — spaced repetition review of learned expressions."""

import random
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.engines.sm2 import quality_from_correct, sm2_calculate
from app.models.expression import Expression
from app.models.memory import UserMemory
from app.models.session import SessionAnswer, StudySession
from app.services.questions import QUESTION_GENERATORS


async def count_due_reviews(user_id: str, db: AsyncSession) -> int:
    """Count how many expressions are due for review."""
    now = datetime.now(timezone.utc)
    stmt = select(func.count(UserMemory.id)).where(
        UserMemory.user_id == user_id,
        UserMemory.next_review_at <= now,
        UserMemory.is_learning == False,
    )
    result = await db.execute(stmt)
    return result.scalar() or 0


async def pick_due_expressions(
    user_id: str,
    word_count: int,
    db: AsyncSession,
) -> list[tuple[UserMemory, Expression]]:
    """Pick expressions due for review, ordered by next_review_at ASC."""
    now = datetime.now(timezone.utc)
    stmt = (
        select(UserMemory, Expression)
        .join(Expression, UserMemory.expression_id == Expression.id)
        .where(
            UserMemory.user_id == user_id,
            UserMemory.next_review_at <= now,
            UserMemory.is_learning == False,
        )
        .order_by(UserMemory.next_review_at.asc())
        .limit(word_count)
    )
    result = await db.execute(stmt)
    return list(result.all())


async def start_review(
    user_id: str,
    word_count: int,
    exercise_types: list[str],
    db: AsyncSession,
) -> tuple[StudySession, list[dict]]:
    """Start a review session: pick due expressions, generate questions."""
    pairs = await pick_due_expressions(user_id, word_count, db)

    if not pairs:
        raise ValueError("Aucune révision due pour le moment. Reviens plus tard !")

    # Create session
    session = StudySession(
        user_id=user_id,
        session_type="review",
        total_questions=len(pairs),
    )
    db.add(session)
    await db.flush()

    # Generate questions cycling through exercise types
    questions = []
    for idx, (memory, expression) in enumerate(pairs):
        q_type = exercise_types[idx % len(exercise_types)]
        generator = QUESTION_GENERATORS.get(q_type)
        if generator is None:
            continue

        if q_type == "MCQ":
            q_data = await generator(expression, db)
        else:
            q_data = generator(expression)

        questions.append({
            "question_id": f"{session.id}:{idx}",
            "expression_id": expression.id,
            "exercise_type": q_type,
            "question": q_data["question"],
            "options": q_data.get("options"),
            "hint": q_data.get("hint"),
        })

    await db.flush()
    return session, questions


async def submit_review_answer(
    session_id: str,
    expression_id: str,
    user_id: str,
    exercise_type: str,
    user_answer: str,
    response_time_ms: int | None,
    db: AsyncSession,
) -> dict:
    """Evaluate a review answer, update SM-2 state, record answer."""
    # Verify session belongs to this user
    sess_result = await db.execute(
        select(StudySession).where(
            StudySession.id == session_id,
            StudySession.user_id == user_id,
        )
    )
    session = sess_result.scalar_one_or_none()
    if not session:
        raise ValueError("Session introuvable")

    # Fetch expression
    expr_result = await db.execute(select(Expression).where(Expression.id == expression_id))
    expression = expr_result.scalar_one_or_none()
    if not expression:
        raise ValueError("Expression introuvable")

    # Fetch current memory
    mem_result = await db.execute(
        select(UserMemory).where(
            UserMemory.user_id == user_id,
            UserMemory.expression_id == expression_id,
        )
    )
    memory = mem_result.scalar_one_or_none()
    if not memory:
        raise ValueError("Aucune mémoire trouvée")

    # Determine correctness based on exercise type
    if exercise_type == "MCQ":
        correct_answer = expression.meaning
        is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
    elif exercise_type == "FILL_BLANK":
        correct_answer = expression.text
        is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
    elif exercise_type == "FR_TO_EN":
        correct_answer = expression.text
        is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
    else:
        correct_answer = expression.meaning
        is_correct = user_answer.strip().lower() == correct_answer.strip().lower()

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
    memory.is_learning = not is_correct

    if is_correct:
        memory.correct_count += 1
        memory.streak += 1
        memory.max_streak = max(memory.max_streak, memory.streak)
    else:
        memory.incorrect_count += 1
        memory.lapses += 1
        memory.streak = 0

    # Schedule next review
    from datetime import timedelta
    memory.next_review_at = now + timedelta(days=result.interval)

    # Record SessionAnswer
    answer = SessionAnswer(
        session_id=session_id,
        expression_id=expression_id,
        user_id=user_id,
        question_type=exercise_type,
        question_data={"type": exercise_type},
        user_answer=user_answer,
        correct_answer=correct_answer,
        is_correct=is_correct,
        response_time_ms=response_time_ms,
    )
    db.add(answer)
    await db.flush()

    return {
        "is_correct": is_correct,
        "correct_answer": correct_answer,
        "quality": quality,
        "mastery_score": result.mastery_score,
        "next_review_at": memory.next_review_at.isoformat() if memory.next_review_at else None,
    }


async def complete_review(session_id: str, user_id: str, db: AsyncSession) -> dict:
    """Finalize a review session."""
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
        "words_reviewed": session.total_questions,
        "correct_count": correct_count,
        "score": score,
        "duration_seconds": duration,
    }
