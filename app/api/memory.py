"""Memory & review API — learning flow and spaced repetition review."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.expression import Expression
from app.models.memory import UserMemory
from app.models.session import SessionAnswer, StudySession
from app.models.user import User
from app.schemas.memory import (
    AnswerSubmission,
    LearningStartRequest,
    ReviewAnswerSubmission,
    ReviewStartRequest,
    SessionComplete,
)
from app.services.learning import (
    complete_learning,
    get_daily_new_word_count,
    pick_new_expressions,
    start_learning,
    submit_learning_answer,
)
from app.services.review import (
    complete_review,
    count_due_reviews,
    start_review,
    submit_review_answer,
)

router = APIRouter(prefix="/api/v1/memory", tags=["memory"])


# ── Dashboard ─────────────────────────────────────────────────────────────────


@router.get("/dashboard")
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return aggregated stats for the current user."""
    # Total expressions learned (not in learning mode)
    learned_result = await db.execute(
        select(func.count(UserMemory.id)).where(
            UserMemory.user_id == current_user.id,
            UserMemory.is_learning == False,
        )
    )
    total_learned = learned_result.scalar() or 0

    # Total memorized (mastery >= 0.8)
    mastered_result = await db.execute(
        select(func.count(UserMemory.id)).where(
            UserMemory.user_id == current_user.id,
            UserMemory.mastery_score >= 0.8,
        )
    )
    total_mastered = mastered_result.scalar() or 0

    # Reviews due today
    due_count = await count_due_reviews(current_user.id, db)

    # Daily streak (max_streak across all memories)
    streak_result = await db.execute(
        select(func.max(UserMemory.max_streak)).where(
            UserMemory.user_id == current_user.id,
        )
    )
    max_streak = streak_result.scalar() or 0

    # New words today
    new_today = await get_daily_new_word_count(current_user.id, db)

    # Total sessions
    sessions_result = await db.execute(
        select(func.count(StudySession.id)).where(
            StudySession.user_id == current_user.id,
            StudySession.status == "completed",
        )
    )
    total_sessions = sessions_result.scalar() or 0

    # Overall accuracy
    correct_result = await db.execute(
        select(func.count(SessionAnswer.id)).where(
            SessionAnswer.user_id == current_user.id,
            SessionAnswer.is_correct == True,
        )
    )
    total_correct = correct_result.scalar() or 0

    total_result = await db.execute(
        select(func.count(SessionAnswer.id)).where(
            SessionAnswer.user_id == current_user.id,
        )
    )
    total_answers = total_result.scalar() or 0
    accuracy = round(total_correct / max(total_answers, 1) * 100, 1)

    return {
        "total_expressions_learned": total_learned,
        "total_mastered": total_mastered,
        "reviews_due_today": due_count,
        "daily_streak": max_streak,
        "new_words_today": new_today,
        "total_sessions": total_sessions,
        "overall_accuracy_pct": accuracy,
    }


# ── Learning Flow ──────────────────────────────────────────────────────────────


@router.get("/learning/next")
async def get_learning_next(
    word_count: int = Query(default=5, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check how many new expressions are available to learn."""
    new_words = await pick_new_expressions(current_user.id, word_count, db)
    today_count = await get_daily_new_word_count(current_user.id, db)

    return {
        "available": len(new_words),
        "learned_today": today_count,
        "sample": [
            {
                "id": e.id,
                "text": e.text,
                "tier": e.tier,
            }
            for e in new_words[:5]
        ],
    }


@router.post("/learning/start", status_code=status.HTTP_201_CREATED)
async def post_learning_start(
    body: LearningStartRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start a learning session with new expressions."""
    try:
        session, cards = await start_learning(current_user.id, body.word_count, db)
        await db.commit()
    except ValueError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return {
        "session_id": session.id,
        "session_type": session.session_type,
        "word_count": len(cards),
        "cards": cards,
    }


@router.post("/learning/submit")
async def post_learning_submit(
    body: AnswerSubmission,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit an answer during a learning session."""
    try:
        result = await submit_learning_answer(
            session_id=body.session_id,
            expression_id=body.expression_id,
            user_id=current_user.id,
            user_answer=body.user_answer,
            response_time_ms=body.response_time_ms,
            db=db,
        )
        await db.commit()
    except ValueError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return result


@router.post("/learning/complete")
async def post_learning_complete(
    body: SessionComplete,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Complete a learning session and get summary."""
    try:
        result = await complete_learning(body.session_id, current_user.id, db)
        await db.commit()
    except ValueError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return result


# ── Review Flow ────────────────────────────────────────────────────────────────


@router.get("/review/today")
async def get_review_today(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check how many expressions are due for review today."""
    due_count = await count_due_reviews(current_user.id, db)
    return {
        "reviews_due": due_count,
        "has_reviews": due_count > 0,
    }


@router.post("/review/start", status_code=status.HTTP_201_CREATED)
async def post_review_start(
    body: ReviewStartRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start a review session with due expressions."""
    types_list = body.exercise_types
    if not types_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one exercise type required",
        )
    valid_types = {"MCQ", "FILL_BLANK", "FR_TO_EN"}
    for t in types_list:
        if t not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid exercise type: {t}. Valid: {valid_types}",
            )

    try:
        session, questions = await start_review(current_user.id, body.word_count, types_list, db)
        await db.commit()
    except ValueError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return {
        "session_id": session.id,
        "session_type": session.session_type,
        "word_count": len(questions),
        "questions": questions,
    }


@router.post("/review/submit")
async def post_review_submit(
    body: ReviewAnswerSubmission,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit an answer during a review session."""
    if body.exercise_type not in {"MCQ", "FILL_BLANK", "FR_TO_EN"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid exercise type: {body.exercise_type}",
        )

    try:
        result = await submit_review_answer(
            session_id=body.session_id,
            expression_id=body.expression_id,
            user_id=current_user.id,
            exercise_type=body.exercise_type,
            user_answer=body.user_answer,
            response_time_ms=body.response_time_ms,
            db=db,
        )
        await db.commit()
    except ValueError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return result


@router.post("/review/complete")
async def post_review_complete(
    body: SessionComplete,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Complete a review session and get summary."""
    try:
        result = await complete_review(body.session_id, current_user.id, db)
        await db.commit()
    except ValueError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return result
