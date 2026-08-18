from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    HTTPException,
    UploadFile,
)

from fastapi.responses import (
    FileResponse,
)

from app.schemas.calibration import (
    CourtCalibrationRequest,
    CourtCalibrationResponse,
)

from app.services.job_calibration import (
    calibrate_processing_job,
)

from app.services.processing_results import (
    get_calibration_frame_path,
)

from app.schemas.video import (
    ProcessingJobResponse,
    VideoUploadResponse,
)

from app.services.processing_jobs import (
    create_processing_job,
    get_processing_job,
    run_computer_vision_job,
)

from app.services.uploads import (
    save_uploaded_video,
)


router = APIRouter(
    prefix="/api/v1/videos",
    tags=["videos"],
)


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
    )

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
                "Calibration frame "
                "was not found."
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