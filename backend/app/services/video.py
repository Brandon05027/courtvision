from pathlib import Path

import cv2


def get_video_metadata(video_path: str) -> dict:
    path = Path(video_path)

    if not path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    capture = cv2.VideoCapture(str(path)) #opens the video

    if not capture.isOpened():
        capture.release()
        raise ValueError(f"Could not open video: {video_path}")

    fps = capture.get(cv2.CAP_PROP_FPS) #How many frame per sec
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT)) #total frame count
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)) 
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    duration_seconds = frame_count / fps if fps > 0 else 0

    capture.release()

    return {
        "fps": round(fps, 2),
        "frame_count": frame_count,
        "width": width,
        "height": height,
        "duration_seconds": round(duration_seconds, 2),
    }

def extract_frames(
    video_path: str,
    output_dir: str,
    target_fps: float = 1.0,
) -> list[str]:
    video = Path(video_path)

    if not video.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    capture = cv2.VideoCapture(str(video))

    if not capture.isOpened():
        capture.release()
        raise ValueError(f"Could not open video: {video_path}")

    source_fps = capture.get(cv2.CAP_PROP_FPS)

    if source_fps <= 0:
        capture.release()
        raise ValueError("Video FPS could not be determined.")

    frame_interval = max(int(round(source_fps / target_fps)), 1) #if the fps is 30 it will be 30/1 = 30 

    saved_frames = []
    frame_number = 0

    while True:
        success, frame = capture.read()

        if not success:
            break

        if frame_number % frame_interval == 0:
            output_path = output / f"frame_{frame_number:06d}.jpg"

            saved = cv2.imwrite(str(output_path), frame)

            if saved:
                saved_frames.append(str(output_path))

        frame_number += 1

    capture.release()

    return saved_frames