from pydantic import BaseModel


class VideoUploadResponse(
    BaseModel
):
    video_id: str
    original_filename: str
    size_bytes: int
    status: str