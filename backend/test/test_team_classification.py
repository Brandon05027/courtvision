import numpy as np

from app.services.team_classification import (
    crop_torso,
    extract_jersey_color,
    calculate_track_color_profiles,
    classify_track_teams,
)


def test_crop_torso_returns_non_empty_image():
    frame = np.zeros(
        (200, 100, 3),
        dtype=np.uint8,
    )

    bounding_box = {
        "x1": 10,
        "y1": 20,
        "x2": 90,
        "y2": 180,
    }

    torso = crop_torso(
        frame,
        bounding_box,
    )

    assert torso.size > 0


def test_extract_jersey_color_returns_three_values():
    image = np.full(
        (50, 50, 3),
        100,
        dtype=np.uint8,
    )

    color = extract_jersey_color(image)

    assert len(color) == 3


def test_calculate_track_color_profiles_uses_median():
    colors_by_track = {
        1: [
            (10.0, 20.0, 30.0),
            (12.0, 22.0, 32.0),
            (100.0, 100.0, 100.0),
        ],
    }

    profiles = calculate_track_color_profiles(
        colors_by_track,
        minimum_samples=3,
    )

    assert profiles[1] == (
        12.0,
        22.0,
        32.0,
    )


def test_track_team_classification():
    profiles = {
        1: (70.5, 140.0, 137.0),
        2: (129.5, 140.0, 129.0),
        3: (91.5, 140.0, 138.0),
        14: (166.5, 133.0, 126.0),
    }

    assignments = classify_track_teams(
        profiles,
        team_a_reference_id=1,
        team_b_reference_id=14,
        unknown_distance_threshold=30.0,
    )

    assert assignments[1]["team"] == "team_a"

    assert assignments[3]["team"] == "team_a"

    assert assignments[14]["team"] == "team_b"

    assert assignments[2]["team"] == "unknown"


def test_missing_reference_player_is_rejected():
    profiles = {
        1: (70.0, 140.0, 137.0),
    }

    try:
        classify_track_teams(
            profiles,
            team_a_reference_id=1,
            team_b_reference_id=99,
        )

        assert False

    except ValueError:
        assert True