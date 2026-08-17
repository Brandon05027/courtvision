import pytest

from app.services.possessions import (
    analyze_possession,
    calculate_pairwise_spacing,
    create_possession,
)


def test_create_possession():
    possession = create_possession(
        possession_id="poss_001",
        team="team_a",
        start_time=5.0,
        end_time=15.0,
        result="missed_shot",
        pass_count=3,
    )

    assert possession[
        "duration_seconds"
    ] == 10.0

    assert possession[
        "pass_count"
    ] == 3


def test_invalid_possession_time_is_rejected():
    with pytest.raises(ValueError):
        create_possession(
            possession_id="poss_001",
            team="team_a",
            start_time=10.0,
            end_time=5.0,
            result="missed_shot",
        )


def test_pairwise_spacing():
    positions = [
        {
            "x": 0.0,
            "y": 0.0,
        },
        {
            "x": 3.0,
            "y": 4.0,
        },
    ]

    spacing = calculate_pairwise_spacing(
        positions
    )

    assert spacing == 5.0

def test_analyze_possession():
    tracks = [
        {
            "track_id": 1,
            "team": "team_a",
            "timestamp_seconds": 1.0,
            "court_position": {
                "x": 0.0,
                "y": 0.0,
            },
        },
        {
            "track_id": 2,
            "team": "team_a",
            "timestamp_seconds": 1.0,
            "court_position": {
                "x": 3.0,
                "y": 4.0,
            },
        },
        {
            "track_id": 1,
            "team": "team_a",
            "timestamp_seconds": 1.5,
            "court_position": {
                "x": 0.0,
                "y": 0.0,
            },
        },
        {
            "track_id": 2,
            "team": "team_a",
            "timestamp_seconds": 1.5,
            "court_position": {
                "x": 6.0,
                "y": 8.0,
            },
        },
    ]

    possession = create_possession(
        possession_id="poss_test",
        team="team_a",
        start_time=1.0,
        end_time=1.5,
        result="missed_shot",
        pass_count=1,
    )

    analysis = analyze_possession(
        possession,
        tracks,
    )

    assert (
        analysis["spacing"][
            "spacing_sample_count"
        ]
        == 2
    )

    assert (
        analysis["spacing"][
            "average_spacing_feet"
        ]
        == 7.5
    )