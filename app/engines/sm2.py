"""SuperMemo SM-2 spaced repetition algorithm.

Quality ratings (0–5):
  0 — complete blackout
  1 — incorrect, but correct answer felt familiar
  2 — incorrect, but correct answer seemed easy to remember
  3 — correct with serious difficulty
  4 — correct after hesitation
  5 — perfect response
"""

from dataclasses import dataclass


SM2_MIN_EF = 1.30
SM2_MAX_EF = 3.00


@dataclass(frozen=True)
class SM2Result:
    """New SRS state after a single review."""

    interval: int          # days until next review
    ease_factor: float     # updated ease factor (clamped [1.3, 3.0])
    repetitions: int       # consecutive correct repetitions
    mastery_score: float   # 0.0 – 1.0


def sm2_calculate(
    quality: int,
    repetitions: int = 0,
    ease_factor: float = 2.50,
    interval: int = 0,
) -> SM2Result:
    """Compute new SM-2 state given a recall quality rating."""

    if quality < 0 or quality > 5:
        raise ValueError(f"quality must be 0–5, got {quality}")

    if ease_factor < SM2_MIN_EF or ease_factor > SM2_MAX_EF:
        raise ValueError(f"ease_factor must be between {SM2_MIN_EF} and {SM2_MAX_EF}")

    # --- Repetitions & Interval ---
    if quality < 3:
        new_repetitions = 0
        new_interval = 1
    else:
        new_repetitions = repetitions + 1
        if new_repetitions == 1:
            new_interval = 1
        elif new_repetitions == 2:
            new_interval = 6
        else:
            new_interval = round(interval * ease_factor)

    # --- Ease Factor ---
    # Per SM-2 spec, EF is only modified on successful recalls (quality >= 3)
    if quality >= 3:
        new_ef = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    else:
        new_ef = ease_factor
    new_ef = max(SM2_MIN_EF, min(SM2_MAX_EF, new_ef))

    # --- Mastery Score (0–1) ---
    raw = (quality / 5.0) * (new_repetitions / (new_repetitions + 5))
    mastery = round(min(1.0, raw), 4)

    return SM2Result(
        interval=new_interval,
        ease_factor=round(new_ef, 2),
        repetitions=new_repetitions,
        mastery_score=mastery,
    )


def quality_from_correct(is_correct: bool, response_time_ms: int | None = None) -> int:
    """Map a binary correct/incorrect + optional response time to a quality rating."""
    if not is_correct:
        return 1
    if response_time_ms is None:
        return 4
    if response_time_ms < 3000:
        return 5
    if response_time_ms < 8000:
        return 4
    return 3
