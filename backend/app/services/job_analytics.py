from collections import defaultdict

from app.services.processing_jobs import (
    get_processing_job,
    update_processing_job,
)

from app.services.processing_results import (
    load_mapped_tracks,
    save_analytics,
)


from collections import defaultdict


MIN_TRACK_OBSERVATIONS = 10 #a track must appear in a 60 inside-court observations before we use it


def calculate_track_distances(
    mapped_tracks: list[dict],
) -> dict[int, float]:
    tracks_by_player = defaultdict(
        list
    )

    for track in mapped_tracks:
        if not track.get(
            "inside_court",
            False,
        ):
            continue

        track_id = track.get(
            "track_id"
        )

        court_position = track.get(
            "court_position"
        )

        if (
            track_id is None
            or court_position is None
        ):
            continue

        tracks_by_player[
            track_id
        ].append(
            (
                track["frame_number"],
                court_position,
            )
        )

    distances = {}

    for (
        track_id,
        positions,
    ) in tracks_by_player.items():

        # Ignore short/noisy tracks
        if (
            len(positions)
            < MIN_TRACK_OBSERVATIONS
        ):
            continue

        positions.sort(
            key=lambda item:
                item[0]
        )

        total_distance = 0.0
        previous = None

        for (
            _,
            position,
        ) in positions:

            if previous is not None:
                dx = (
                    position["x"]
                    - previous["x"]
                )

                dy = (
                    position["y"]
                    - previous["y"]
                )

                total_distance += (
                    dx * dx
                    + dy * dy
                ) ** 0.5

            previous = position

        distances[
            track_id
        ] = round(
            total_distance,
            2,
        )

    return distances


def build_basic_analytics(
    job_id: str,
) -> dict:
    job = get_processing_job(
        job_id
    )

    mapped_tracks = (
        load_mapped_tracks(
            job_id
        )
    )

    distances = (
        calculate_track_distances(
                mapped_tracks
            )
        )

    track_ids = sorted(
        distances.keys()
        )

    inside_court_tracks = [
        track
        for track in mapped_tracks
        if track.get(
            "inside_court",
            False,
        )
    ]

    analytics = {
        "job_id": job_id,
        "video_id": job[
            "video_id"
        ],
        "unique_track_count":
            len(track_ids),
        "mapped_record_count":
            len(mapped_tracks),
        "inside_court_record_count":
            len(
                inside_court_tracks
            ),
        "player_distances_feet": {
            str(track_id):
                distance
            for (
                track_id,
                distance
            ) in distances.items()
        },
    }

    path = save_analytics(
        job_id,
        analytics,
    )

    job[
        "analytics_path"
    ] = path

    update_processing_job(
        job_id,
        status="processing",
        stage="analytics",
        progress=90,
        message=(
            "Movement analytics "
            "generated successfully."
        ),
    )

    return analytics