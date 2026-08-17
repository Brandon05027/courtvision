from math import hypot


HOOP_X = 25.0
HOOP_Y = 5.25


VALID_SHOT_RESULTS = {
    "made",
    "missed",
}


def create_shot(
    track_id: int,
    timestamp_seconds: float,
    court_x: float,
    court_y: float,
    result: str,
    team: str | None = None,
) -> dict:
    if result not in VALID_SHOT_RESULTS:
        raise ValueError(
            f"Invalid shot result: {result}"
        )

    return {
        "track_id": track_id,
        "timestamp_seconds": round(
            timestamp_seconds,
            3,
        ),
        "court_position": {
            "x": round(court_x, 2),
            "y": round(court_y, 2),
        },
        "result": result,
        "team": team,
        "manually_confirmed": True,
    }

def find_nearest_player_position(
    tracks: list[dict],
    track_id: int,
    timestamp_seconds: float,
) -> dict:
    player_tracks = [
        track
        for track in tracks
        if track["track_id"] == track_id
    ]

    if not player_tracks:
        raise ValueError(
            f"No tracking data for Track ID {track_id}."
        )

    nearest = min(
        player_tracks,
        key=lambda track: abs(
            track["timestamp_seconds"]
            - timestamp_seconds
        ),
    )

    return nearest

def create_shot_from_track(
    tracks: list[dict],
    track_id: int,
    timestamp_seconds: float,
    result: str,
    team: str | None = None,
) -> dict:
    nearest = find_nearest_player_position(
        tracks,
        track_id,
        timestamp_seconds,
    )

    position = nearest["court_position"]

    return create_shot(
        track_id=track_id,
        timestamp_seconds=timestamp_seconds,
        court_x=position["x"],
        court_y=position["y"],
        result=result,
        team=team,
    )

def classify_shot_type(
    court_x: float,
    court_y: float,
) -> str:
    distance_from_hoop = hypot(
        court_x - HOOP_X,
        court_y - HOOP_Y,
    )

    if distance_from_hoop <= 8:
        return "paint"

    if distance_from_hoop >= 23:
        return "three_pointer"

    return "mid_range"