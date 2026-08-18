from app.services.processing_jobs import (
    get_processing_job,
)

from app.services.processing_results import (
    load_mapped_tracks,
)

from app.services.team_classification import (
    calculate_track_color_profiles,
    collect_track_jersey_colors,
    classify_track_teams,
)


def build_team_profiles(
    job_id: str,
) -> dict:
    job = get_processing_job(
        job_id
    )

    tracks = load_mapped_tracks(
        job_id
    )

    video_path = job.get(
        "video_path"
    )

    if not video_path:
        raise ValueError(
            "Original video path is unavailable for this job."
        )

    colors_by_track = (
        collect_track_jersey_colors(
            video_path,
            tracks,
            sample_every_n_frames=5,
        )
    )

    profiles = (
        calculate_track_color_profiles(
            colors_by_track,
            minimum_samples=3,
        )
    )

    return {
        "profiles": profiles,
        "track_count": len(
            profiles
        ),
    }


def assign_job_teams(
    job_id: str,
    team_a_reference_id: int,
    team_b_reference_id: int,
) -> dict:
    result = build_team_profiles(
        job_id
    )

    profiles = result[
        "profiles"
    ]

    assignments = (
        classify_track_teams(
            profiles,
            team_a_reference_id,
            team_b_reference_id,
            unknown_distance_threshold=50.0,
        )
    )

    return assignments