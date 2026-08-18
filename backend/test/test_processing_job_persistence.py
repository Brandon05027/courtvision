from app.services import (
    processing_jobs,
)


def test_processing_job_persistence(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        processing_jobs,
        "JOB_RESULTS_DIRECTORY",
        tmp_path,
    )

    job = {
        "job_id": "test-job",
        "video_id": "test-video",
        "video_path": "uploads/test.mp4",
        "status": "processing",
        "stage": "tracking",
        "progress": 60,
        "message": "Tracking players.",
        "error": None,
        "created_at": "test",
        "updated_at": "test",
    }

    processing_jobs.save_processing_job(
        job
    )

    loaded = (
        processing_jobs
        .load_processing_job(
            "test-job"
        )
    )

    assert (
        loaded["video_id"]
        == "test-video"
    )

    assert (
        loaded["video_path"]
        == "uploads/test.mp4"
    )

    assert (
        loaded["progress"]
        == 60
    )