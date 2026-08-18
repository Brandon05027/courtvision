from app.services import (
    processing_results,
)


def test_save_and_load_tracks(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        processing_results,
        "RESULTS_DIRECTORY",
        tmp_path,
    )

    tracks = [
        {
            "track_id": 1,
            "frame_number": 10,
        },
        {
            "track_id": 2,
            "frame_number": 10,
        },
    ]

    processing_results.save_tracks(
        "job-test",
        tracks,
    )

    loaded = (
        processing_results
        .load_tracks(
            "job-test"
        )
    )

    assert loaded == tracks


def test_tracking_video_path(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        processing_results,
        "RESULTS_DIRECTORY",
        tmp_path,
    )

    path = (
        processing_results
        .get_tracking_video_path(
            "job-test"
        )
    )

    assert (
        path.name
        == "tracked_video.mp4"
    )