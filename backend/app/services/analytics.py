from math import hypot


def calculate_distance(
    first_position: dict,
    second_position: dict,
) -> float:
    dx = second_position["x"] - first_position["x"]
    dy = second_position["y"] - first_position["y"]

    return hypot(dx, dy) #This will calulate the distance using the formula √(dx² + dy²)

def calculate_player_movement(
    player_tracks: list[dict],
    max_reasonable_speed: float = 30.0, #Prevent outliers that gives a ridiculous ans
) -> dict:
    if len(player_tracks) < 2:
        return {
            "distance_traveled_feet": 0.0,
            "average_speed_ft_s": 0.0,
            "maximum_speed_ft_s": 0.0,
            "tracked_duration_seconds": 0.0,
            "position_count": len(player_tracks),
        }

    ordered_tracks = sorted(
        player_tracks,
        key=lambda track: track["timestamp_seconds"],
    )

    total_distance = 0.0
    valid_duration = 0.0
    speeds = []

    for previous, current in zip(
        ordered_tracks,
        ordered_tracks[1:],
    ):
        time_difference = (
            current["timestamp_seconds"]
            - previous["timestamp_seconds"]
        )

        if time_difference <= 0:
            continue

        distance = calculate_distance(
            previous["court_position"],
            current["court_position"],
        )

        speed = distance / time_difference

        if speed > max_reasonable_speed:
            continue

        total_distance += distance
        valid_duration += time_difference
        speeds.append(speed)

    average_speed = (
        total_distance / valid_duration
        if valid_duration > 0
        else 0.0
    )

    maximum_speed = max(speeds) if speeds else 0.0

    return {
        "distance_traveled_feet": round(total_distance, 2),
        "average_speed_ft_s": round(average_speed, 2),
        "maximum_speed_ft_s": round(maximum_speed, 2),
        "tracked_duration_seconds": round(valid_duration, 2),
        "position_count": len(ordered_tracks),
    }

def calculate_all_player_movements(
    players: dict[int, list[dict]],
) -> dict[int, dict]:
    analytics = {}

    for track_id, tracks in players.items():
        analytics[track_id] = calculate_player_movement(
            tracks
        )

    return analytics

def calculate_tracking_coverage(
    player_tracks: list[dict],
    video_duration_seconds: float,
) -> float:
    if not player_tracks or video_duration_seconds <= 0:
        return 0.0

    timestamps = [
        track["timestamp_seconds"]
        for track in player_tracks
    ]

    tracked_duration = max(timestamps) - min(timestamps)

    coverage = (
        tracked_duration
        / video_duration_seconds
        * 100
    )

    return round(min(coverage, 100.0), 2)