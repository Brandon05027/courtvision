from pathlib import Path

import cv2
from ultralytics import YOLO

PERSON_CLASS_ID = 0

# Analyze one frame out of every five.
# 30 FPS video -> approximately 6 analyzed FPS.
DEFAULT_FRAME_STRIDE = 5


class PlayerTracker:
    def __init__(self, model_name: str = "yolo26n.pt"):
        self.model = YOLO(model_name)

    def track_video(
        self,
        video_path: str,
        output_path: str,
        confidence_threshold: float = 0.4,
        frame_stride: int = DEFAULT_FRAME_STRIDE,
    ) -> dict:
        video = Path(video_path)

        if not video.exists():
            raise FileNotFoundError(
                f"Video not found: {video_path}"
            )

        if frame_stride < 1:
            raise ValueError(
                "frame_stride must be at least 1"
            )

        capture = cv2.VideoCapture(str(video))

        if not capture.isOpened():
            capture.release()
            raise ValueError(
                f"Could not open video: {video_path}"
            )

        fps = capture.get(cv2.CAP_PROP_FPS)
        width = int(
            capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        )
        height = int(
            capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        )

        output = Path(output_path)
        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # We only write analyzed frames, so reduce
        # the output FPS to preserve approximately
        # the same video duration.
        output_fps = (
            fps / frame_stride
            if fps > 0
            else 6.0
        )

        writer = cv2.VideoWriter(
            str(output),
            cv2.VideoWriter_fourcc(*"mp4v"),
            output_fps,
            (width, height),
        )

        if not writer.isOpened():
            capture.release()
            writer.release()
            raise ValueError(
                f"Could not create output video: {output_path}"
            )

        tracks = []

        frame_number = 0
        processed_frame_count = 0

        try:
            while True:
                success, frame = capture.read()

                if not success:
                    break

                # Skip expensive YOLO inference
                # for frames we do not need.
                if frame_number % frame_stride != 0:
                    frame_number += 1
                    continue

                timestamp_seconds = (
                    frame_number / fps
                    if fps > 0
                    else 0
                )

                results = self.model.track(
                    source=frame,
                    persist=True,
                    tracker="bytetrack.yaml",
                    classes=[PERSON_CLASS_ID],
                    conf=confidence_threshold,
                    verbose=False,
                )

                result = results[0]

                if (
                    result.boxes is not None
                    and result.boxes.id is not None
                ):
                    boxes = (
                        result.boxes.xyxy
                        .cpu()
                        .tolist()
                    )

                    track_ids = (
                        result.boxes.id
                        .int()
                        .cpu()
                        .tolist()
                    )

                    confidences = (
                        result.boxes.conf
                        .cpu()
                        .tolist()
                    )

                    for (
                        box,
                        track_id,
                        confidence,
                    ) in zip(
                        boxes,
                        track_ids,
                        confidences,
                    ):
                        x1, y1, x2, y2 = box

                        center_x = (
                            x1 + x2
                        ) / 2

                        bottom_y = y2

                        tracks.append(
                            {
                                "frame_number": frame_number,
                                "timestamp_seconds": round(
                                    timestamp_seconds,
                                    3,
                                ),
                                "track_id": track_id,
                                "confidence": round(
                                    float(confidence),
                                    4,
                                ),
                                "bounding_box": {
                                    "x1": round(x1, 2),
                                    "y1": round(y1, 2),
                                    "x2": round(x2, 2),
                                    "y2": round(y2, 2),
                                },
                                "court_contact_point": {
                                    "x": round(
                                        center_x,
                                        2,
                                    ),
                                    "y": round(
                                        bottom_y,
                                        2,
                                    ),
                                },
                            }
                        )

                        cv2.rectangle(
                            frame,
                            (
                                int(x1),
                                int(y1),
                            ),
                            (
                                int(x2),
                                int(y2),
                            ),
                            (0, 255, 0),
                            2,
                        )

                        cv2.putText(
                            frame,
                            (
                                f"ID {track_id} "
                                f"{confidence:.2f}"
                            ),
                            (
                                int(x1),
                                max(
                                    int(y1) - 10,
                                    0,
                                ),
                            ),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 255, 0),
                            2,
                        )

                        cv2.circle(
                            frame,
                            (
                                int(center_x),
                                int(bottom_y),
                            ),
                            5,
                            (0, 0, 255),
                            -1,
                        )

                writer.write(frame)

                processed_frame_count += 1
                frame_number += 1

        finally:
            capture.release()
            writer.release()

        return {
            "output_path": str(output),
            "frame_count": frame_number,
            "processed_frame_count": processed_frame_count,
            "frame_stride": frame_stride,
            "tracks": tracks,
        }