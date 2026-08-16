import pytest

from app.services.analytics import (
    calculate_distance,
    calculate_player_movement,
    calculate_tracking_coverage,
)


def test_calculate_distance():
    distance = calculate_distance(
        {"x": 0, "y": 0},
        {"x": 3, "y": 4},
    )

    assert distance == pytest.approx(5.0)


def test_calculate_player_movement():
    tracks = [
        {
            "timestamp_seconds": 0.0,
            "court_position": {
                "x": 0.0,
                "y": 0.0,
            },
        },
        {
            "timestamp_seconds": 1.0,
            "court_position": {
                "x": 3.0,
                "y": 4.0,
            },
        },
        {
            "timestamp_seconds": 2.0,
            "court_position": {
                "x": 6.0,
                "y": 8.0,
            },
        },
    ]

    analytics = calculate_player_movement(tracks)

    assert analytics["distance_traveled_feet"] == 10.0
    assert analytics["average_speed_ft_s"] == 5.0
    assert analytics["maximum_speed_ft_s"] == 5.0
    assert analytics["tracked_duration_seconds"] == 2.0
    assert analytics["position_count"] == 3


def test_tracking_coverage():
    tracks = [
        {
            "timestamp_seconds": 2.0,
        },
        {
            "timestamp_seconds": 8.0,
        },
    ]

    coverage = calculate_tracking_coverage(
        tracks,
        video_duration_seconds=10.0,
    )

    assert coverage == 60.0


def test_unrealistic_speed_is_rejected():
    tracks = [
        {
            "timestamp_seconds": 0.0,
            "court_position": {
                "x": 0.0,
                "y": 0.0,
            },
        },
        {
            "timestamp_seconds": 0.1,
            "court_position": {
                "x": 50.0,
                "y": 47.0,
            },
        },
    ]

    analytics = calculate_player_movement(
        tracks,
        max_reasonable_speed=30.0,
    )

    assert analytics["distance_traveled_feet"] == 0.0
    assert analytics["average_speed_ft_s"] == 0.0