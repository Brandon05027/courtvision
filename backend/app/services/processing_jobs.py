import uuid
from datetime import datetime, timezone
from pathlib import Path
import cv2

from app.services.processing_results import (
    get_calibration_frame_path,
    get_tracking_video_path,
    save_tracks,
)   

from app.services.tracking import (
    PlayerTracker,
)

UPLOAD_DIRECTORY = Path("uploads")


JOBS: dict[str, dict] = {}


PROCESSING_STAGES = [
    "uploaded",
    "preparing",
    "ready_for_analysis",
    "detection",
    "tracking",
    "calibration",
    "mapping",
    "analytics",
    "summary",
    "completed",
]


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def find_uploaded_video(
    video_id: str,
) -> Path:
    matches = list(
        UPLOAD_DIRECTORY.glob(
            f"{video_id}.*"
        )
    )

    if not matches:
        raise ValueError(
            "Uploaded video was not found."
        )

    return matches[0]


def create_processing_job(
    video_id: str,
) -> dict:
    video_path = find_uploaded_video(
        video_id
    )

    job_id = str(
        uuid.uuid4()
    )

    job = {
        "job_id": job_id,
        "video_id": video_id,
        "status": "queued",
        "stage": "uploaded",
        "progress": 10,
        "message": "Video uploaded successfully.",
        "video_path": str(video_path),
        "error": None,
        "created_at": utc_now(),
        "updated_at": utc_now(),
    }

    JOBS[job_id] = job

    return job


def get_processing_job(
    job_id: str,
) -> dict:
    job = JOBS.get(
        job_id
    )

    if job is None:
        raise ValueError(
            "Processing job was not found."
        )

    return job


def update_processing_job(
    job_id: str,
    *,
    status: str | None = None,
    stage: str | None = None,
    progress: int | None = None,
    message: str | None = None,
    error: str | None = None,
) -> dict:
    job = get_processing_job(
        job_id
    )

    if status is not None:
        job["status"] = status

    if stage is not None:
        job["stage"] = stage

    if progress is not None:
        job["progress"] = max(
            0,
            min(
                progress,
                100,
            ),
        )

    if message is not None:
        job["message"] = message

    if error is not None:
        job["error"] = error

    job["updated_at"] = utc_now()

    return job

def prepare_video_job(
    job_id: str,
) -> None:
    try:
        job = get_processing_job(
            job_id
        )

        update_processing_job(
            job_id,
            status="processing",
            stage="preparing",
            progress=30,
            message="Preparing uploaded video.",
        )

        video_path = Path(
            job["video_path"]
        )

        if not video_path.exists():
            raise ValueError(
                "Uploaded video file is missing."
            )

        file_size = (
            video_path.stat().st_size
        )

        if file_size <= 0:
            raise ValueError(
                "Uploaded video is empty."
            )

        update_processing_job(
            job_id,
            status="ready",
            stage="ready_for_analysis",
            progress=40,
            message=(
                "Video is ready for "
                "computer vision analysis."
            ),
        )

    except Exception as exc:
        update_processing_job(
            job_id,
            status="failed",
            progress=0,
            message="Video preparation failed.",
            error=str(exc),
        )

def run_computer_vision_job(
    job_id: str,
) -> None:
    try:
        job = get_processing_job(
            job_id
        )

        video_path = Path(
            job["video_path"]
        )

        if not video_path.exists():
            raise ValueError(
                "Uploaded video file is missing."
            )

        update_processing_job(
            job_id,
            status="processing",
            stage="detection",
            progress=50,
            message=(
                "Detecting players in "
                "the uploaded video."
            ),
        )

        tracker = PlayerTracker()

        tracking_output_path = (
            get_tracking_video_path(
                job_id
            )
        )

        update_processing_job(
            job_id,
            stage="tracking",
            progress=60,
            message=(
                "Detecting and tracking "
                "players across frames."
            ),
        )

        result = tracker.track_video(
            str(video_path),
            str(tracking_output_path),
        )

        tracks = result.get(
            "tracks",
            []
        )

        capture = cv2.VideoCapture(
            str(video_path)
        )

        success, frame = capture.read()

        capture.release()

        if not success:
            raise ValueError(
                "Could not create "
                "calibration frame."
            )

        calibration_frame_path = (
            get_calibration_frame_path(
                job_id
            )
        )

        cv2.imwrite(
            str(calibration_frame_path),
            frame,
        )

        job[
            "calibration_frame_path"
        ] = str(
            calibration_frame_path
        )

        if not tracks:
            raise ValueError(
                "No player tracks were produced."
            )

        tracks_path = save_tracks(
            job_id,
            tracks,
        )

        job[
            "tracking_output_path"
        ] = str(
            tracking_output_path
        )

        job[
            "tracks_path"
        ] = tracks_path

        job[
            "track_record_count"
        ] = len(
            tracks
        )

        unique_track_ids = {
            track["track_id"]
            for track in tracks
            if "track_id" in track
        }

        job[
            "unique_track_count"
        ] = len(
            unique_track_ids
        )

        update_processing_job(
            job_id,
            status="review_required",
            stage="calibration",
            progress=70,
            message=(
                "Player tracking complete. "
                "Court calibration is required "
                "before analytics can continue."
            ),
        )

    except Exception as exc:
        update_processing_job(
            job_id,
            status="failed",
            progress=0,
            message=(
                "Computer vision "
                "processing failed."
            ),
            error=str(exc),
        )