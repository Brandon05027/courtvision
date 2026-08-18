from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
)

from app.schemas.video import (
    VideoUploadResponse,
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