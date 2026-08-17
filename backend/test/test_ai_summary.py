import pytest

from app.services.ai_summary import (
    PossessionSummary,
    create_fallback_summary,
    possession_summary_to_dict,
    validate_evidence_keys,
)


def get_sample_analysis():
    return {
        "possession_id": "poss_001",
        "team": "team_a",
        "start_time": 5.0,
        "end_time": 15.0,
        "duration_seconds": 10.0,
        "result": "missed_shot",
        "pass_count": 3,
        "manually_segmented": True,
        "spacing": {
            "average_spacing_feet": 14.8,
            "minimum_spacing_feet": 11.2,
            "maximum_spacing_feet": 18.4,
            "spacing_sample_count": 20,
        },
    }


def test_create_fallback_summary():
    analysis = get_sample_analysis()

    summary = create_fallback_summary(
        analysis
    )

    assert isinstance(
        summary,
        PossessionSummary,
    )

    assert (
        summary.summary
        == "team_a had a 10.0-second possession ending in missed_shot."
    )

    assert (
        summary.positive
        == "Average offensive spacing was 14.8 feet."
    )

    assert (
        summary.improvement
        == "Minimum spacing reached 11.2 feet."
    )

    assert "duration_seconds" in summary.evidence_keys
    assert "result" in summary.evidence_keys
    assert "average_spacing_feet" in summary.evidence_keys
    assert "minimum_spacing_feet" in summary.evidence_keys


def test_summary_converts_to_dict():
    summary = PossessionSummary(
        summary="Test summary",
        positive="Test positive",
        improvement="Test improvement",
        evidence_keys=[
            "result",
        ],
    )

    result = possession_summary_to_dict(
        summary
    )

    assert result["summary"] == "Test summary"
    assert result["positive"] == "Test positive"
    assert result["improvement"] == "Test improvement"

    assert result["evidence_keys"] == [
        "result"
    ]


def test_valid_evidence_keys_are_accepted():
    validate_evidence_keys(
        [
            "duration_seconds",
            "result",
            "pass_count",
            "average_spacing_feet",
        ]
    )


def test_invalid_evidence_key_is_rejected():
    with pytest.raises(ValueError):
        validate_evidence_keys(
            [
                "duration_seconds",
                "two_defenders_collapsed",
            ]
        )