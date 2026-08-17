import pytest

from app.services.shots import (
    classify_shot_type,
    create_shot,
    find_nearest_player_position,
)


def test_create_shot():
    shot = create_shot(
        track_id=7,
        timestamp_seconds=5.5,
        court_x=25.0,
        court_y=10.0,
        result="made",
        team="team_a",
    )

    assert shot["track_id"] == 7
    assert shot["result"] == "made"
    assert shot["manually_confirmed"] is True


def test_invalid_shot_result_is_rejected():
    with pytest.raises(ValueError):
        create_shot(
            track_id=7,
            timestamp_seconds=5.5,
            court_x=25.0,
            court_y=10.0,
            result="banana",
        )


def test_find_nearest_player_position():
    tracks = [
        {
            "track_id": 7,
            "timestamp_seconds": 1.0,
            "court_position": {
                "x": 10.0,
                "y": 10.0,
            },
        },
        {
            "track_id": 7,
            "timestamp_seconds": 2.0,
            "court_position": {
                "x": 20.0,
                "y": 20.0,
            },
        },
    ]

    nearest = find_nearest_player_position(
        tracks,
        track_id=7,
        timestamp_seconds=1.8,
    )

    assert nearest["timestamp_seconds"] == 2.0


def test_classify_shot_type():
    assert classify_shot_type(
        25.0,
        8.0,
    ) == "paint"