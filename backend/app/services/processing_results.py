import json

from pathlib import Path


RESULTS_DIRECTORY = Path(
    "output/jobs"
)


def create_job_output_directory(
    job_id: str,
) -> Path:
    output_directory = (
        RESULTS_DIRECTORY
        / job_id
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return output_directory


def get_tracking_video_path(
    job_id: str,
) -> Path:
    output_directory = (
        create_job_output_directory(
            job_id
        )
    )

    return (
        output_directory
        / "tracked_video.mp4"
    )


def get_tracks_path(
    job_id: str,
) -> Path:
    output_directory = (
        create_job_output_directory(
            job_id
        )
    )

    return (
        output_directory
        / "tracks.json" #save it so it wont disappear when we close python
    )


def save_tracks(
    job_id: str,
    tracks: list[dict],
) -> str:
    path = get_tracks_path(
        job_id
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            tracks,
            file,
            indent=2,
        )

    return str(path)


def load_tracks(
    job_id: str,
) -> list[dict]:
    path = get_tracks_path(
        job_id
    )

    if not path.exists():
        raise ValueError(
            "Tracking results were not found."
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        tracks = json.load(
            file
        )

    return tracks

def get_calibration_frame_path(
    job_id: str,
) -> Path:
    output_directory = (
        create_job_output_directory(
            job_id
        )
    )

    return (
        output_directory
        / "calibration_frame.jpg"
    )


def get_mapped_tracks_path(
    job_id: str,
) -> Path:
    output_directory = (
        create_job_output_directory(
            job_id
        )
    )

    return (
        output_directory
        / "mapped_tracks.json"
    )


def save_mapped_tracks(
    job_id: str,
    tracks: list[dict],
) -> str:
    path = get_mapped_tracks_path(
        job_id
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            tracks,
            file,
            indent=2,
        )

    return str(path)


def load_mapped_tracks(
    job_id: str,
) -> list[dict]:
    path = get_mapped_tracks_path(
        job_id
    )

    if not path.exists():
        raise ValueError(
            "Mapped tracking results "
            "were not found."
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)