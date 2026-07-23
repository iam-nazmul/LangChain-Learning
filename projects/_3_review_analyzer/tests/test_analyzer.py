import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from schema import ReviewAnalysis
from analyze import analyze_review, TOOL_NAME

FIXTURES_PATH = Path(__file__).parent / "fixtures" / "reviews.json"


def _make_tool_response(rating: int, sentiment: str, confidence: float, summary: str):
    """Build a minimal mock anthropic.Message with a tool_use block."""
    block = MagicMock()
    block.type = "tool_use"
    block.name = TOOL_NAME
    block.input = {
        "rating": rating,
        "sentiment": sentiment,
        "confidence": confidence,
        "summary": summary,
    }
    response = MagicMock()
    response.content = [block]
    response.stop_reason = "tool_use"
    return response


# ── Schema unit tests ────────────────────────────────────────────────────────

class TestReviewAnalysisSchema:
    def test_valid_positive(self):
        r = ReviewAnalysis(rating=5, sentiment="positive", confidence=0.95, summary="Great product.")
        assert r.rating == 5
        assert r.sentiment == "positive"

    def test_valid_negative(self):
        r = ReviewAnalysis(rating=1, sentiment="negative", confidence=0.9, summary="Terrible.")
        assert r.rating == 1

    def test_valid_neutral(self):
        r = ReviewAnalysis(rating=3, sentiment="neutral", confidence=0.6, summary="It's okay.")
        assert r.sentiment == "neutral"

    def test_rating_bounds(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            ReviewAnalysis(rating=0, sentiment="neutral", confidence=0.5, summary="x")
        with pytest.raises(ValidationError):
            ReviewAnalysis(rating=6, sentiment="neutral", confidence=0.5, summary="x")

    def test_confidence_bounds(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            ReviewAnalysis(rating=3, sentiment="neutral", confidence=1.1, summary="x")
        with pytest.raises(ValidationError):
            ReviewAnalysis(rating=3, sentiment="neutral", confidence=-0.1, summary="x")

    def test_invalid_sentiment(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            ReviewAnalysis(rating=3, sentiment="excellent", confidence=0.5, summary="x")


# ── Mocked analyzer unit tests ───────────────────────────────────────────────

class TestAnalyzeReviewMocked:
    @patch("analyze.anthropic.Anthropic")
    def test_returns_review_analysis(self, MockAnthropic):
        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = _make_tool_response(
            rating=5, sentiment="positive", confidence=0.98, summary="Excellent product."
        )
        result = analyze_review("This product is amazing!")
        assert isinstance(result, ReviewAnalysis)
        assert result.rating == 5
        assert result.sentiment == "positive"

    @patch("analyze.anthropic.Anthropic")
    def test_retry_on_validation_failure(self, MockAnthropic):
        from pydantic import ValidationError

        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client

        bad_block = MagicMock()
        bad_block.type = "tool_use"
        bad_block.name = TOOL_NAME
        bad_block.input = {"rating": 99, "sentiment": "positive", "confidence": 0.9, "summary": "ok"}
        bad_response = MagicMock()
        bad_response.content = [bad_block]
        bad_response.stop_reason = "tool_use"

        good_response = _make_tool_response(4, "positive", 0.9, "Good product.")

        mock_client.messages.create.side_effect = [bad_response, good_response]
        result = analyze_review("Pretty good!", mock_client)
        assert result.rating == 4
        assert mock_client.messages.create.call_count == 2

    @patch("analyze.anthropic.Anthropic")
    def test_raises_on_double_validation_failure(self, MockAnthropic):
        from pydantic import ValidationError

        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client

        bad_block = MagicMock()
        bad_block.type = "tool_use"
        bad_block.name = TOOL_NAME
        bad_block.input = {"rating": 99, "sentiment": "invalid", "confidence": 99.0, "summary": "x"}
        bad_response = MagicMock()
        bad_response.content = [bad_block]
        bad_response.stop_reason = "tool_use"

        mock_client.messages.create.return_value = bad_response
        with pytest.raises(ValidationError):
            analyze_review("Test review.", mock_client)

    @patch("analyze.anthropic.Anthropic")
    def test_no_silent_default_on_missing_tool_call(self, MockAnthropic):
        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client

        text_block = MagicMock()
        text_block.type = "text"
        bad_response = MagicMock()
        bad_response.content = [text_block]
        bad_response.stop_reason = "end_turn"

        mock_client.messages.create.return_value = bad_response
        with pytest.raises(ValueError, match=TOOL_NAME):
            analyze_review("Some review.", mock_client)


# ── Fixture-driven regression tests ─────────────────────────────────────────

@pytest.mark.parametrize("fixture", json.loads(FIXTURES_PATH.read_text()))
@patch("analyze.anthropic.Anthropic")
def test_fixture_reviews_schema_valid(MockAnthropic, fixture):
    """Every fixture review must produce a schema-valid ReviewAnalysis."""
    mock_client = MagicMock()
    MockAnthropic.return_value = mock_client
    mock_client.messages.create.return_value = _make_tool_response(
        rating=fixture["expected_rating"],
        sentiment=fixture["expected_sentiment"],
        confidence=0.9,
        summary="Mock summary.",
    )
    result = analyze_review(fixture["text"], mock_client)
    assert isinstance(result, ReviewAnalysis)
    assert 1 <= result.rating <= 5
    assert result.sentiment in ("positive", "neutral", "negative")
    assert 0.0 <= result.confidence <= 1.0
    assert result.summary
