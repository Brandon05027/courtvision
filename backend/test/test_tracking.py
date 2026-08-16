import pytest

from app.services.tracking import PlayerTracker


def test_missing_tracking_video_is_rejected():
    tracker = PlayerTracker.__new__(PlayerTracker)

    with pytest.raises(FileNotFoundError):
        tracker.track_video(
            "missing-video.mp4",
            "output.mp4",
        )