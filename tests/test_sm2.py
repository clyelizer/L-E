"""Unit tests for the SM-2 spaced repetition engine."""

import pytest
from app.engines.sm2 import SM2_MIN_EF, SM2_MAX_EF, sm2_calculate, quality_from_correct


class TestSM2Calculate:
    def test_first_review_perfect(self):
        """Quality 5 on first review → interval=1, reps=1, ef increases to 2.60."""
        result = sm2_calculate(quality=5)
        assert result.interval == 1
        assert result.repetitions == 1
        assert result.ease_factor == 2.60  # EF' = 2.50 + 0.1 = 2.60 for quality=5
        assert result.mastery_score > 0

    def test_second_review_good(self):
        """Quality 4 on second review → interval=6, reps=2."""
        result = sm2_calculate(quality=4, repetitions=1, ease_factor=2.50, interval=1)
        assert result.interval == 6
        assert result.repetitions == 2

    def test_third_review_perfect(self):
        """Quality 5 on third review → interval=round(6*2.5)=15, reps=3."""
        result = sm2_calculate(quality=5, repetitions=2, ease_factor=2.50, interval=6)
        assert result.interval == 15
        assert result.repetitions == 3

    def test_failed_recall_resets(self):
        """Quality <3 → repetitions=0, interval=1."""
        result = sm2_calculate(quality=1, repetitions=5, ease_factor=2.50, interval=30)
        assert result.repetitions == 0
        assert result.interval == 1
        assert result.mastery_score < 0.1

    def test_ease_factor_unchanged_on_failed_recall(self):
        """Quality <3 → EF unchanged per SM-2 spec (only modified on quality >= 3)."""
        result = sm2_calculate(quality=0, repetitions=3, ease_factor=2.50, interval=10)
        assert result.ease_factor == 2.50

    def test_ease_factor_decreases_on_low_quality_3(self):
        """Quality 3 (minimum successful recall) → EF decreases from 2.50.
        EF' = 2.5 + (0.1 - (5-3)*(0.08 + (5-3)*0.02))
           = 2.5 + (0.1 - 2*(0.08 + 2*0.02))
           = 2.5 + (0.1 - 2*(0.08 + 0.04))
           = 2.5 + (0.1 - 2*0.12)
           = 2.5 + (0.1 - 0.24)
           = 2.5 + (-0.14)
           = 2.36
        """
        result = sm2_calculate(quality=3, repetitions=3, ease_factor=2.50, interval=10)
        assert result.ease_factor == pytest.approx(2.36, abs=0.01)

    def test_ease_factor_increases_on_high_score(self):
        """Quality 5 → EF increases from 2.50."""
        result = sm2_calculate(quality=5, repetitions=3, ease_factor=2.50, interval=10)
        assert result.ease_factor > 2.50

    def test_ease_factor_floor(self):
        """EF cannot go below 1.30 no matter how bad the score."""
        result = sm2_calculate(quality=0, repetitions=10, ease_factor=1.30, interval=30)
        assert result.ease_factor == SM2_MIN_EF

    def test_ease_factor_ceiling(self):
        """EF cannot go above 3.00 no matter how good the score."""
        result = sm2_calculate(quality=5, repetitions=10, ease_factor=3.00, interval=30)
        assert result.ease_factor == SM2_MAX_EF

    def test_consecutive_failures(self):
        """Multiple quality <3: reps reset, interval=1, EF unchanged per SM-2 spec."""
        r1 = sm2_calculate(quality=1, repetitions=0, ease_factor=2.50, interval=0)
        r2 = sm2_calculate(quality=2, repetitions=r1.repetitions, ease_factor=r1.ease_factor, interval=r1.interval)
        assert r2.repetitions == 0
        assert r2.interval == 1
        assert r2.ease_factor == 2.50  # unchanged: quality < 3

    def test_mastery_score_grows_with_reps(self):
        """More successful repetitions → higher mastery."""
        r1 = sm2_calculate(quality=4, repetitions=0, ease_factor=2.50, interval=0)
        r2 = sm2_calculate(quality=4, repetitions=r1.repetitions, ease_factor=r1.ease_factor, interval=r1.interval)
        r3 = sm2_calculate(quality=4, repetitions=r2.repetitions, ease_factor=r2.ease_factor, interval=r2.interval)
        assert r1.mastery_score < r2.mastery_score < r3.mastery_score

    def test_quality_out_of_range(self):
        """Quality >5 or <0 raises ValueError."""
        with pytest.raises(ValueError):
            sm2_calculate(quality=6)
        with pytest.raises(ValueError):
            sm2_calculate(quality=-1)

    def test_ef_out_of_range(self):
        """EF outside valid range raises ValueError."""
        with pytest.raises(ValueError):
            sm2_calculate(quality=4, ease_factor=1.00)
        with pytest.raises(ValueError):
            sm2_calculate(quality=4, ease_factor=3.50)


class TestQualityFromCorrect:
    def test_incorrect_returns_1(self):
        assert quality_from_correct(False) == 1

    def test_correct_no_time_returns_4(self):
        assert quality_from_correct(True) == 4

    def test_correct_fast_returns_5(self):
        assert quality_from_correct(True, 2000) == 5

    def test_correct_medium_returns_4(self):
        assert quality_from_correct(True, 5000) == 4

    def test_correct_slow_returns_3(self):
        assert quality_from_correct(True, 10000) == 3

    # --- Boundary tests ---

    def test_correct_at_0ms(self):
        """0ms response time → below 3000ms threshold → quality 5."""
        assert quality_from_correct(True, 0) == 5

    def test_correct_at_3000ms(self):
        """3000ms response → not < 3000ms, but < 8000ms → quality 4."""
        assert quality_from_correct(True, 3000) == 4

    def test_correct_at_8000ms(self):
        """8000ms response → not < 3000ms, not < 8000ms → quality 3."""
        assert quality_from_correct(True, 8000) == 3

    def test_incorrect_fast(self):
        """Incorrect even with very fast response → quality 1."""
        assert quality_from_correct(False, 100) == 1
