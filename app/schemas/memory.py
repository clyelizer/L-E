"""SRS memory, session, and quiz Pydantic schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


# ─── Learning ───

class LearningNextResponse(BaseModel):
    available_count: int
    daily_limit: int
    used_today: int


class LearningStartRequest(BaseModel):
    word_count: int = Field(default=5, ge=1, le=20)


class LearningCard(BaseModel):
    expression_id: str
    text: str
    meaning: str
    image_path: str | None = None
    example_sentence: str | None = None
    metaphor: str | None = None


class LearningSubmitRequest(BaseModel):
    session_id: str
    expression_id: str
    answer: str
    response_time_ms: int | None = None


class LearningCompleteRequest(BaseModel):
    session_id: str


class LearningCompleteResponse(BaseModel):
    session_id: str
    words_learned: int
    score: float
    avg_response_time_ms: float | None = None


# ─── POST body models (replace Query params) ───

class AnswerSubmission(BaseModel):
    """Body model for submitting an answer during a learning session."""
    session_id: str
    expression_id: str
    user_answer: str = Field(..., min_length=1, description="User's answer")
    response_time_ms: int | None = Field(default=None, ge=0, description="Response time in ms")


class ReviewAnswerSubmission(AnswerSubmission):
    """Body model for submitting an answer during a review session."""
    exercise_type: str = Field(..., description="Exercise type (MCQ/FILL_BLANK/FR_TO_EN)")


class SessionComplete(BaseModel):
    """Body model for completing a session."""
    session_id: str


# ─── Review ───

class ReviewTodayResponse(BaseModel):
    available_count: int
    due_expressions: list[dict]


class ReviewStartRequest(BaseModel):
    word_count: int = Field(default=20, ge=1, le=100)
    exercise_types: list[str] = Field(default=["MCQ", "FILL_BLANK", "FR_TO_EN"])


class ReviewQuestion(BaseModel):
    question_id: str
    expression_id: str
    exercise_type: str
    question: str
    options: list[str] | None = None  # For MCQ
    hint: str | None = None


class ReviewSubmitRequest(BaseModel):
    session_id: str
    expression_id: str
    exercise_type: str
    answer: str
    response_time_ms: int | None = None


class ReviewSubmitResponse(BaseModel):
    is_correct: bool
    correct_answer: str
    explanation: str | None = None


class ReviewCompleteRequest(BaseModel):
    session_id: str


class ReviewCompleteResponse(BaseModel):
    session_id: str
    words_reviewed: int
    correct_count: int
    score: float
    duration_seconds: int


# ─── Quiz ───

class QuizGenerateRequest(BaseModel):
    expression_id: str
    question_type: str  # MCQ, FILL_BLANK, FR_TO_EN, EN_TO_FR
    count: int = Field(default=1, ge=1, le=5)


class QuizAnswerRequest(BaseModel):
    question_id: str
    answer: str


# ─── Progress ───

class DashboardResponse(BaseModel):
    streak: int
    reviewed_today: int
    review_target: int
    learned_today: int
    new_words_target: int
    mastery_overall: float
    mastery_distribution: dict
    weakest_expressions: list[dict]


class WeaknessItem(BaseModel):
    expression_id: str
    text: str
    error_type: str
    mastery_score: float
    times_repeated: int


class ProgressHistoryItem(BaseModel):
    date: str
    reviewed: int
    correct: int
    score: float
    new_words: int


class MasteryItem(BaseModel):
    expression_id: str
    text: str
    tier: int | None = None
    mastery_score: float
    interval_hours: int
    next_review: datetime | None = None
    is_learning: bool
