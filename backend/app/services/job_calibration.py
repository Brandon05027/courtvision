from app.services.calibration import (
    calculate_homography,
)

from app.services.mapping import (
    map_tracks_to_court,
)

from app.services.processing_jobs import (
    get_processing_job,
    update_processing_job,
)

from app.services.processing_results import (
    load_tracks,
    save_mapped_tracks,
)


COURT_POINTS = [
    [0.0, 0.0],
    [50.0, 0.0],
    [50.0, 47.0],
    [0.0, 47.0],
]


def calibrate_processing_job(
    job_id: str,
    image_points: list[
        list[float]
    ],
) -> dict:
    if len(image_points) != 4:
        raise ValueError(
            "Exactly four court "
            "points are required."
        )

    job = get_processing_job(
        job_id
    )

    tracks = load_tracks(
        job_id
    )

    matrix = calculate_homography(
        image_points,
        COURT_POINTS,
    )

    mapped_tracks = (
        map_tracks_to_court(
            tracks,
            matrix,
        )
    )

    if not mapped_tracks:
        raise ValueError(
            "No tracks could be "
            "mapped to the court."
        )

    mapped_path = (
        save_mapped_tracks(
            job_id,
            mapped_tracks,
        )
    )

    inside_court_count = sum(
        1
        for track in mapped_tracks
        if track.get(
            "inside_court",
            False,
        )
    )

    job[
        "mapped_tracks_path"
    ] = mapped_path

    job[
        "mapped_track_count"
    ] = len(
        mapped_tracks
    )

    job[
        "inside_court_count"
    ] = inside_court_count

    job[
        "image_points"
    ] = image_points

    job[
        "court_points"
    ] = COURT_POINTS

    update_processing_job(
        job_id,
        status="processing",
        stage="mapping",
        progress=80,
        message=(
            "Court calibrated and "
            "player positions mapped."
        ),
    )

    return job