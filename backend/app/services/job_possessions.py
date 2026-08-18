from math import sqrt
from uuid import uuid4

from app.services.processing_results import (
    load_mapped_tracks,
)


def calculate_spacing_metrics(
    track_records: list[dict],
) -> dict:
    positions_by_frame: dict[
        int,
        list[tuple[float, float]],
    ] = {}

    for record in track_records:
        frame_number = record.get(
            "frame_number"
        )

        court_position = record.get(
            "court_position"
        )

        if (
            frame_number is None
            or not court_position
        ):
            continue

        x = court_position.get("x")
        y = court_position.get("y")

        if x is None or y is None:
            continue

        positions_by_frame.setdefault(
            frame_number,
            [],
        ).append(
            (
                float(x),
                float(y),
            )
        )

    frame_spacings = []

    for positions in (
        positions_by_frame.values()
    ):
        if len(positions) < 2:
            continue

        distances = []

        for index_a in range(
            len(positions)
        ):
            for index_b in range(
                index_a + 1,
                len(positions),
            ):
                x1, y1 = (
                    positions[index_a]
                )

                x2, y2 = (
                    positions[index_b]
                )

                distance = sqrt(
                    (x2 - x1) ** 2
                    + (y2 - y1) ** 2
                )

                distances.append(
                    distance
                )

        if distances:
            frame_spacings.append(
                sum(distances)
                / len(distances)
            )

    if not frame_spacings:
        return {
            "average_spacing_feet":
                None,
            "minimum_spacing_feet":
                None,
            "maximum_spacing_feet":
                None,
        }

    return {
        "average_spacing_feet":
            round(
                sum(frame_spacings)
                / len(
                    frame_spacings
                ),
                2,
            ),
        "minimum_spacing_feet":
            round(
                min(
                    frame_spacings
                ),
                2,
            ),
        "maximum_spacing_feet":
            round(
                max(
                    frame_spacings
                ),
                2,
            ),
    }


def build_reviewed_possession(
    job_id: str,
    start_time: float,
    end_time: float,
    result: str,
    pass_count: int = 0,
    fps: float = 30.0,
) -> dict:
    if end_time <= start_time:
        raise ValueError(
            "Possession end time must "
            "be after start time."
        )

    allowed_results = {
        "made_shot",
        "missed_shot",
        "no_shot",
    }

    if result not in allowed_results:
        raise ValueError(
            "Invalid possession result."
        )

    if pass_count < 0:
        raise ValueError(
            "Pass count cannot be "
            "negative."
        )

    mapped_tracks = load_mapped_tracks(
        job_id
    )

    start_frame = int(
        start_time * fps
    )

    end_frame = int(
        end_time * fps
    )

    possession_tracks = [
        record
        for record in mapped_tracks
        if (
            start_frame
            <= record.get(
                "frame_number",
                -1,
            )
            <= end_frame
            and record.get(
                "inside_court",
                False,
            )
        )
    ]

    spacing = (
        calculate_spacing_metrics(
            possession_tracks
        )
    )

    duration_seconds = round(
        end_time - start_time,
        2,
    )

    return {
        "possession_id":
            str(uuid4()),
        "start_time":
            start_time,
        "end_time":
            end_time,
        "duration_seconds":
            duration_seconds,
        "result":
            result,
        "pass_count":
            pass_count,
        "average_spacing_feet":
            spacing[
                "average_spacing_feet"
            ],
        "minimum_spacing_feet":
            spacing[
                "minimum_spacing_feet"
            ],
        "maximum_spacing_feet":
            spacing[
                "maximum_spacing_feet"
            ],
        "track_records":
            possession_tracks,
    }