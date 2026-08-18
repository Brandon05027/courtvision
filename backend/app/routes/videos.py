from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    HTTPException,
    UploadFile,
)

from app.schemas.possession import (
    PossessionReviewRequest,
    PossessionReviewResponse,
)

from app.services.job_possessions import (
    build_reviewed_possession,
)

from fastapi.responses import (
    FileResponse,
)

from app.schemas.analytics import (
    JobAnalyticsResponse,
    TeamClassificationRequest,
    TeamClassificationResponse,
)

from app.services.visualization import (
    save_job_movement_heatmap,
)

from app.schemas.calibration import (
    CourtCalibrationRequest,
    CourtCalibrationResponse,
)

from app.schemas.video import (
    ProcessingJobResponse,
    VideoUploadResponse,
)

from app.services.job_analytics import (
    build_basic_analytics,
)

from app.services.job_calibration import (
    calibrate_processing_job,
)

from app.services.job_team_classification import (
    assign_job_teams,
    build_team_profiles,
)

from app.services.processing_jobs import (
    create_processing_job,
    get_processing_job,
    reset_job_to_calibration,
    run_computer_vision_job,
)

from app.services.processing_results import (
    get_calibration_frame_path,
    get_tracking_video_path,
    get_web_tracking_video_path,
    get_movement_heatmap_path,
)

from app.services.uploads import (
    save_uploaded_video,
)


router = APIRouter(
    prefix="/api/v1/videos",
    tags=["videos"],
)


# =========================================================
# Upload video
# =========================================================

@router.post(
    "/upload",
    response_model=VideoUploadResponse,
)
async def upload_video(
    video: UploadFile = File(...),
) -> VideoUploadResponse:
    try:
        result = await save_uploaded_video(
            video
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return VideoUploadResponse(
        video_id=result[
            "video_id"
        ],
        original_filename=result[
            "original_filename"
        ],
        size_bytes=result[
            "size_bytes"
        ],
        status=result[
            "status"
        ],
    )


# =========================================================
# Start processing
# =========================================================

@router.post(
    "/{video_id}/process",
    response_model=ProcessingJobResponse,
)
async def process_video(
    video_id: str,
    background_tasks: BackgroundTasks,
) -> ProcessingJobResponse:
    try:
        job = create_processing_job(
            video_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    background_tasks.add_task(
        run_computer_vision_job,
        job["job_id"],
    )

    return ProcessingJobResponse(
        job_id=job["job_id"],
        video_id=job["video_id"],
        status=job["status"],
        stage=job["stage"],
        progress=job["progress"],
        message=job["message"],
        error=job["error"],
        track_record_count=job.get(
            "track_record_count"
        ),
        unique_track_count=job.get(
            "unique_track_count"
        ),
    )


# =========================================================
# Get processing job status
# =========================================================

@router.get(
    "/jobs/{job_id}",
    response_model=ProcessingJobResponse,
)
async def processing_job_status(
    job_id: str,
) -> ProcessingJobResponse:
    try:
        job = get_processing_job(
            job_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return ProcessingJobResponse(
        job_id=job["job_id"],
        video_id=job["video_id"],
        status=job["status"],
        stage=job["stage"],
        progress=job["progress"],
        message=job["message"],
        error=job["error"],
        track_record_count=job.get(
            "track_record_count"
        ),
        unique_track_count=job.get(
            "unique_track_count"
        ),
    )


# =========================================================
# Calibration frame
# =========================================================

@router.get(
    "/jobs/{job_id}/calibration-frame"
)
async def calibration_frame(
    job_id: str,
):
    try:
        get_processing_job(
            job_id
        )

        frame_path = (
            get_calibration_frame_path(
                job_id
            )
        )

        if not frame_path.exists():
            raise ValueError(
                "Calibration frame was not found."
            )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return FileResponse(
        frame_path,
        media_type="image/jpeg",
    )


# =========================================================
# Calibrate court
# =========================================================

@router.post(
    "/jobs/{job_id}/calibrate",
    response_model=(
        CourtCalibrationResponse
    ),
)
async def calibrate_job(
    job_id: str,
    request: CourtCalibrationRequest,
) -> CourtCalibrationResponse:
    try:
        image_points = [
            [
                point.x,
                point.y,
            ]
            for point
            in request.image_points
        ]

        job = (
            calibrate_processing_job(
                job_id,
                image_points,
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return CourtCalibrationResponse(
        job_id=job["job_id"],
        status=job["status"],
        stage=job["stage"],
        progress=job["progress"],
        mapped_track_count=job[
            "mapped_track_count"
        ],
        inside_court_count=job[
            "inside_court_count"
        ],
        message=job["message"],
    )


# =========================================================
# Reset calibration
# =========================================================

@router.post(
    "/jobs/{job_id}/reset-calibration"
)
async def reset_calibration(
    job_id: str,
):
    try:
        job = (
            reset_job_to_calibration(
                job_id
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return job


# =========================================================
# Analytics
# =========================================================

@router.post(
    "/jobs/{job_id}/analytics",
    response_model=JobAnalyticsResponse,
)
async def generate_job_analytics(
    job_id: str,
) -> JobAnalyticsResponse:
    try:
        analytics = (
            build_basic_analytics(
                job_id
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return JobAnalyticsResponse(
        **analytics
    )


# =========================================================
# Team classification
# =========================================================

@router.post(
    "/jobs/{job_id}/teams",
    response_model=(
        TeamClassificationResponse
    ),
)
async def classify_job_teams(
    job_id: str,
    request: TeamClassificationRequest,
) -> TeamClassificationResponse:
    try:
        assignments = (
            assign_job_teams(
                job_id,
                request.team_a_reference_id,
                request.team_b_reference_id,
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    cleaned = {
        str(track_id): {
            "team":
                assignment[
                    "team"
                ],
            "distance_to_team_a":
                assignment[
                    "distance_to_team_a"
                ],
            "distance_to_team_b":
                assignment[
                    "distance_to_team_b"
                ],
        }
        for (
            track_id,
            assignment
        ) in assignments.items()
    }

    return (
        TeamClassificationResponse(
            assignments=cleaned
        )
    )


# =========================================================
# Tracked video
# =========================================================

@router.get(
    "/jobs/{job_id}/tracked-video"
)
async def tracked_video(
    job_id: str,
):
    try:
        get_processing_job(
            job_id
        )

        video_path = (
            get_tracking_video_path(
                job_id
            )
        )

        web_video_path = (
            video_path.parent /
            "tracked_video_web.mp4"
        )

        if web_video_path.exists():
            video_path = web_video_path

        if not video_path.exists():
            raise ValueError(
                "Tracked video was not found."
            )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return FileResponse(
        video_path,
        media_type="video/mp4",
    )

@router.get(
    "/jobs/{job_id}/tracked-video"
)
async def tracked_video(
    job_id: str,
):
    try:
        get_processing_job(
            job_id
        )

        video_path = (
            get_web_tracking_video_path(
                job_id
            )
        )

        if not video_path.exists():
            raise ValueError(
                "Browser-compatible "
                "tracked video was "
                "not found."
            )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return FileResponse(
        video_path,
        media_type="video/mp4",
        headers={
            "Cache-Control":
                "no-store",
        },
    )

@router.get(
    "/jobs/{job_id}/team-profiles"
)
async def get_team_profiles(
    job_id: str,
):
    try:
        result = build_team_profiles(
            job_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    profiles = result["profiles"]

    return {
        "track_ids": sorted(
            int(track_id)
            for track_id
            in profiles.keys()
        ),
        "track_count": len(
            profiles
        ),
    }

@router.get(
    "/jobs/{job_id}/movement-heatmap"
)
async def movement_heatmap(
    job_id: str,
):
    try:
        get_processing_job(
            job_id
        )

        heatmap_path = (
            get_movement_heatmap_path(
                job_id
            )
        )

        if not heatmap_path.exists():
            heatmap_path = (
                save_job_movement_heatmap(
                    job_id
                )
            )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return FileResponse(
        heatmap_path,
        media_type="image/png",
        headers={
            "Cache-Control":
                "no-store",
        },
    )

@router.post(
    "/jobs/{job_id}/possession-review",
    response_model=(
        PossessionReviewResponse
    ),
)
async def review_possession(
    job_id: str,
    request:
        PossessionReviewRequest,
) -> PossessionReviewResponse:
    try:
        result = (
            build_reviewed_possession(
                job_id,
                request.start_time,
                request.end_time,
                request.result,
                request.pass_count,
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return (
        PossessionReviewResponse(
            possession_id=result[
                "possession_id"
            ],
            start_time=result[
                "start_time"
            ],
            end_time=result[
                "end_time"
            ],
            duration_seconds=result[
                "duration_seconds"
            ],
            result=result[
                "result"
            ],
            pass_count=result[
                "pass_count"
            ],
            average_spacing_feet=
                result[
                    "average_spacing_feet"
                ],
            minimum_spacing_feet=
                result[
                    "minimum_spacing_feet"
                ],
            maximum_spacing_feet=
                result[
                    "maximum_spacing_feet"
                ],
        )
    )