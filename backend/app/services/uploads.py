import uuid

from pathlib import Path

from fastapi import UploadFile


ALLOWED_VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".avi",
    ".mkv",
}


MAX_VIDEO_SIZE_BYTES = (
    100 * 1024 * 1024
)


UPLOAD_DIRECTORY = Path(
    "uploads"
)


def validate_video_filename(
    filename: str,
) -> None:
    extension = Path(
        filename
    ).suffix.lower()

    if (
        extension
        not in ALLOWED_VIDEO_EXTENSIONS
    ):
        raise ValueError(
            "Unsupported video format."
        )


def create_video_id() -> str:
    return str(
        uuid.uuid4()
    )


async def save_uploaded_video(
    upload: UploadFile,
) -> dict:
    if upload.filename is None:
        raise ValueError(
            "Uploaded video must have a filename."
        )

    validate_video_filename(
        upload.filename
    )

    video_id = create_video_id()

    extension = Path(
        upload.filename
    ).suffix.lower()

    UPLOAD_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination = (
        UPLOAD_DIRECTORY
        / f"{video_id}{extension}"
    )

    total_size = 0

    with destination.open(
        "wb"
    ) as output_file:

        while True:
            chunk = await upload.read(
                1024 * 1024
            )

            if not chunk:
                break

            total_size += len(
                chunk
            )

            if (
                total_size
                > MAX_VIDEO_SIZE_BYTES
            ):
                output_file.close()

                destination.unlink(
                    missing_ok=True
                )

                raise ValueError(
                    "Video exceeds the "
                    "100 MB upload limit."
                )

            output_file.write(
                chunk
            )

    return {
        "video_id": video_id,
        "original_filename": (
            upload.filename
        ),
        "stored_path": str(
            destination
        ),
        "size_bytes": total_size,
        "status": "uploaded",
    }