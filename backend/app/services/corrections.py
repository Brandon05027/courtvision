from datetime import datetime, timezone


VALID_TEAM_LABELS = {
    "team_a",
    "team_b",
    "unknown",
    "ignore",
}


def apply_team_correction(
    assignments: dict[int, dict],
    track_id: int,
    corrected_team: str,
) -> dict[int, dict]:
    if corrected_team not in VALID_TEAM_LABELS:
        raise ValueError(
            f"Invalid team label: {corrected_team}"
        )

    if track_id not in assignments:
        raise KeyError(
            f"Track ID {track_id} does not exist."
        )

    corrected_assignments = {
        key: value.copy()
        for key, value in assignments.items()
    }

    current = corrected_assignments[track_id]

    original_team = current.get(
        "original_team",
        current["team"],
    )

    current["original_team"] = original_team
    current["team"] = corrected_team
    current["manually_corrected"] = True
    current["corrected_at"] = (
        datetime.now(timezone.utc).isoformat()
    )

    return corrected_assignments

def apply_assignments_to_tracks(
    tracks: list[dict],
    assignments: dict[int, dict],
    exclude_ignored: bool = True,
) -> list[dict]:
    updated_tracks = []

    for track in tracks:
        track_id = track["track_id"]

        assignment = assignments.get(track_id)

        if assignment is None:
            team = "unknown"
        else:
            team = assignment["team"]

        if exclude_ignored and team == "ignore":
            continue

        updated_track = {
            **track,
            "team": team,
        }

        updated_tracks.append(
            updated_track
        )

    return updated_tracks

def create_team_correction_record(
    track_id: int,
    original_team: str,
    corrected_team: str,
) -> dict:
    return {
        "track_id": track_id,
        "original_team": original_team,
        "corrected_team": corrected_team,
        "corrected_at": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),
    }