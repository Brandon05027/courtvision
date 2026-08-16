import numpy as np

from app.services.calibration import transform_point


def map_tracks_to_court(
    tracks: list[dict],
    homography_matrix: np.ndarray,
    court_width: float = 50.0,
    court_length: float = 47.0,
) -> list[dict]:
    mapped_tracks = []

    for track in tracks:
        contact_point = track["court_contact_point"]

        image_x = contact_point["x"]
        image_y = contact_point["y"]

        court_x, court_y = transform_point(
            (image_x, image_y),
            homography_matrix,
        )

        mapped_track = {
            **track, #take existed area from track and add other fields
            "court_position": {
                "x": court_x,
                "y": court_y,
            },
            "inside_court": ( #we want to avoid some random audiences, coach, ref as much as possible 
                0 <= court_x <= court_width
                and 0 <= court_y <= court_length
            ),
        }

        mapped_tracks.append(mapped_track)

    return mapped_tracks

def group_tracks_by_player(
    tracks: list[dict],
    inside_court_only: bool = True,
) -> dict[int, list[dict]]:
    players: dict[int, list[dict]] = {}

    for track in tracks:
        if inside_court_only and not track["inside_court"]:
            continue

        track_id = track["track_id"]

        if track_id not in players:
            players[track_id] = []

        players[track_id].append(track)

    return players