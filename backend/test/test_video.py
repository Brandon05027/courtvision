#The fake video test is easier to perform it repeatedly on the computer since we already know the number.

import cv2
import numpy as np

from app.services.video import extract_frames
from app.services.video import get_video_metadata
from pathlib import Path


def test_get_video_metadata(tmp_path):
    video_path = tmp_path / "test_video.mp4"

    width = 320
    height = 240
    fps = 10
    frame_count = 20

    writer = cv2.VideoWriter(
        str(video_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )

    for _ in range(frame_count):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        writer.write(frame)

    writer.release()

    metadata = get_video_metadata(str(video_path))

    assert metadata["fps"] == fps
    assert metadata["frame_count"] == frame_count
    assert metadata["width"] == width
    assert metadata["height"] == height
    assert metadata["duration_seconds"] == 2.0

def test_extract_frames(tmp_path):
    video_path = tmp_path / "test_video.mp4"
    output_dir = tmp_path / "frames"

    width = 320
    height = 240
    fps = 10
    frame_count = 20

    writer = cv2.VideoWriter(
        str(video_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )

    for _ in range(frame_count):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        writer.write(frame)

    writer.release()

    frames = extract_frames(
        str(video_path),
        str(output_dir),
        target_fps=1,
    )

    assert len(frames) == 2

    for frame_path in frames:
        assert Path(frame_path).exists()