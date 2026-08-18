from pydantic import BaseModel


class VideoUploadResponse(
    BaseModel
):
    video_id: str
    original_filename: str
    size_bytes: int
    status: str

class ProcessingJobResponse(
    BaseModel
):
    job_id: str
    video_id: str
    status: str
    stage: str
    progress: int
    message: str
    error: str | None = None
    track_record_count: int | None = None
    unique_track_count: int | None = None