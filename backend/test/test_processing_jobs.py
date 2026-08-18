from pathlib import Path

import pytest

from app.services import (
    processing_jobs,
)


def test_create_processing_job(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        processing_jobs,
        "UPLOAD_DIRECTORY",
        tmp_path,
    )

    video_id = "test-video"

    video_path = (
        tmp_path
        / f"{video_id}.mp4"
    )

    video_path.write_bytes(
        b"video-data"
    )

    job = (
        processing_jobs
        .create_processing_job(
            video_id
        )
    )

    assert (
        job["video_id"]
        == video_id
    )

    assert (
        job["status"]
        == "queued"
    )

    assert (
        job["stage"]
        == "uploaded"
    )


def test_missing_video_rejected(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        processing_jobs,
        "UPLOAD_DIRECTORY",
        tmp_path,
    )

    with pytest.raises(
        ValueError
    ):
        processing_jobs\
            .create_processing_job(
                "missing-video"
            )