import numpy as np

from app.services.mapping import (
    group_tracks_by_player,
    map_tracks_to_court,
)


def test_map_tracks_to_court():
    homography = np.array(
        [
            [0.5, 0.0, 0.0],
            [0.0, 0.47, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float32,
    )

    tracks = [
        {
            "frame_number": 0,
            "timestamp_seconds": 0.0,
            "track_id": 1,
            "confidence": 0.9,
            "court_contact_point": {
                "x": 100.0,
                "y": 100.0,
            },
        }
    ]

    mapped = map_tracks_to_court(
        tracks,
        homography,
    )

    assert len(mapped) == 1

    assert mapped[0]["court_position"]["x"] == 50.0
    assert mapped[0]["court_position"]["y"] == 47.0
    assert mapped[0]["inside_court"] is True

def test_group_tracks_by_player():
    tracks = [
        {
            "track_id": 1,
            "inside_court": True,
        },
        {
            "track_id": 1,
            "inside_court": True,
        },
        {
            "track_id": 2,
            "inside_court": True,
        },
    ]

    players = group_tracks_by_player(tracks)

    assert len(players[1]) == 2
    assert len(players[2]) == 1