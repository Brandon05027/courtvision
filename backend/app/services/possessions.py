from itertools import combinations
from math import hypot


VALID_POSSESSION_RESULTS = {
    "made_shot",
    "missed_shot",
    "turnover",
    "other",
}


def create_possession(
    possession_id: str,
    team: str,
    start_time: float,
    end_time: float,
    result: str,
    pass_count: int = 0,
) -> dict:
    if end_time <= start_time:
        raise ValueError(
            "Possession end time must be after start time."
        )

    if result not in VALID_POSSESSION_RESULTS:
        raise ValueError(
            f"Invalid possession result: {result}"
        )

    if pass_count < 0:
        raise ValueError(
            "Pass count cannot be negative."
        )

    return {
        "possession_id": possession_id,
        "team": team,
        "start_time": round(start_time, 3),
        "end_time": round(end_time, 3),
        "duration_seconds": round(
            end_time - start_time,
            3,
        ),
        "result": result,
        "pass_count": pass_count,
        "manually_segmented": True,
    }

def calculate_pairwise_spacing(
    positions: list[dict],
) -> float:
    if len(positions) < 2:
        return 0.0

    distances = []

    for first, second in combinations(
        positions,
        2,
    ):
        dx = second["x"] - first["x"]
        dy = second["y"] - first["y"]

        distance = hypot(dx, dy)

        distances.append(distance)

    return round(
        sum(distances) / len(distances),
        2,
    )

def get_team_positions_at_time(
    tracks: list[dict],
    team: str,
    timestamp_seconds: float,
    tolerance_seconds: float = 0.15,
) -> list[dict]:
    closest_by_player = {}

    for track in tracks:
        if track.get("team") != team:
            continue

        time_difference = abs(
            track["timestamp_seconds"]
            - timestamp_seconds
        )

        if time_difference > tolerance_seconds:
            continue

        track_id = track["track_id"]

        previous = closest_by_player.get(
            track_id
        )

        if (
            previous is None
            or time_difference
            < previous["time_difference"]
        ):
            closest_by_player[track_id] = {
                "time_difference": time_difference,
                "position": track[
                    "court_position"
                ],
            }

    return [
        item["position"]
        for item in closest_by_player.values()
    ]

def calculate_team_spacing_at_time(
    tracks: list[dict],
    team: str,
    timestamp_seconds: float,
    tolerance_seconds: float = 0.15,
) -> dict:
    positions = get_team_positions_at_time(
        tracks,
        team,
        timestamp_seconds,
        tolerance_seconds,
    )

    spacing = calculate_pairwise_spacing(
        positions
    )

    return {
        "timestamp_seconds": round(
            timestamp_seconds,
            3,
        ),
        "player_count": len(positions),
        "average_spacing_feet": spacing,
    }

def calculate_possession_spacing(
    tracks: list[dict],
    team: str,
    start_time: float,
    end_time: float,
    sample_interval: float = 0.5,
) -> dict:
    if end_time <= start_time:
        raise ValueError(
            "End time must be after start time."
        )

    samples = []

    current_time = start_time

    while current_time <= end_time:
        sample = calculate_team_spacing_at_time(
            tracks,
            team,
            current_time,
        )

        if sample["player_count"] >= 2:
            samples.append(sample)

        current_time += sample_interval

    if not samples:
        return {
            "average_spacing_feet": 0.0,
            "minimum_spacing_feet": 0.0,
            "maximum_spacing_feet": 0.0,
            "spacing_sample_count": 0,
        }

    values = [
        sample["average_spacing_feet"]
        for sample in samples
    ]

    return {
        "average_spacing_feet": round(
            sum(values) / len(values),
            2,
        ),
        "minimum_spacing_feet": round(
            min(values),
            2,
        ),
        "maximum_spacing_feet": round(
            max(values),
            2,
        ),
        "spacing_sample_count": len(values),
    }
def analyze_possession(
    possession: dict,
    tracks: list[dict],
) -> dict:
    spacing = calculate_possession_spacing(
        tracks,
        possession["team"],
        possession["start_time"],
        possession["end_time"],
    )

    return {
        **possession,
        "spacing": spacing,
    }