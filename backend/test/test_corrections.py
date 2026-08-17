import pytest

from app.services.corrections import (
    apply_assignments_to_tracks,
    apply_team_correction,
)


def test_apply_team_correction():
    assignments = {
        1: {
            "team": "team_a",
        },
        2: {
            "team": "unknown",
        },
    }

    corrected = apply_team_correction(
        assignments,
        track_id=2,
        corrected_team="ignore",
    )

    assert corrected[2]["team"] == "ignore"

    assert (
        corrected[2]["original_team"]
        == "unknown"
    )

    assert (
        corrected[2]["manually_corrected"]
        is True
    )


def test_invalid_team_correction_is_rejected():
    assignments = {
        1: {
            "team": "team_a",
        },
    }

    with pytest.raises(ValueError):
        apply_team_correction(
            assignments,
            track_id=1,
            corrected_team="banana",
        )


def test_unknown_track_id_is_rejected():
    assignments = {
        1: {
            "team": "team_a",
        },
    }

    with pytest.raises(KeyError):
        apply_team_correction(
            assignments,
            track_id=99,
            corrected_team="team_b",
        )
def test_ignored_track_is_removed():
    tracks = [
        {
            "track_id": 1,
        },
        {
            "track_id": 2,
        },
    ]

    assignments = {
        1: {
            "team": "team_a",
        },
        2: {
            "team": "ignore",
        },
    }

    updated = apply_assignments_to_tracks(
        tracks,
        assignments,
    )

    assert len(updated) == 1
    assert updated[0]["track_id"] == 1
    assert updated[0]["team"] == "team_a"