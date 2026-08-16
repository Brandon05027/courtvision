from pathlib import Path

import cv2
from ultralytics import YOLO

PERSON_CLASS_ID = 0


class PlayerTracker:
    def __init__(self, model_name: str = "yolo26n.pt"):
        self.model = YOLO(model_name)

    def track_video(
        self,
        video_path: str,
        output_path: str,
        confidence_threshold: float = 0.4,
    ) -> dict:
        video = Path(video_path)

        if not video.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        capture = cv2.VideoCapture(str(video))

        if not capture.isOpened():
            capture.release()
            raise ValueError(f"Could not open video: {video_path}")

        fps = capture.get(cv2.CAP_PROP_FPS)
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        writer = cv2.VideoWriter(
            str(output),
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (width, height),
        )

        tracks = []
        frame_number = 0

        while True:
            success, frame = capture.read()

            if not success:
                break

            timestamp_seconds = (
                frame_number / fps
                if fps > 0
                else 0
            )

            results = self.model.track( #Track and check if it's the same person
                source=frame,
                persist=True,
                tracker="bytetrack.yaml",
                classes=[PERSON_CLASS_ID],
                conf=confidence_threshold,
                verbose=False,
            )

            result = results[0]

            if result.boxes is not None and result.boxes.id is not None:
                boxes = result.boxes.xyxy.cpu().tolist()
                track_ids = result.boxes.id.int().cpu().tolist()
                confidences = result.boxes.conf.cpu().tolist()

                for box, track_id, confidence in zip(
                    boxes,
                    track_ids,
                    confidences,
                ):
                    x1, y1, x2, y2 = box

                    center_x = (x1 + x2) / 2
                    bottom_y = y2

                    tracks.append(
                        {
                            "frame_number": frame_number,
                            "timestamp_seconds": round(timestamp_seconds, 3),
                            "track_id": track_id,
                            "confidence": round(float(confidence), 4),
                            "bounding_box": {
                                "x1": round(x1, 2),
                                "y1": round(y1, 2),
                                "x2": round(x2, 2),
                                "y2": round(y2, 2),
                            },
                            "court_contact_point": {
                                "x": round(center_x, 2),
                                "y": round(bottom_y, 2),
                            },
                        }
                    )

                    cv2.rectangle(
                        frame,
                        (int(x1), int(y1)),
                        (int(x2), int(y2)),
                        (0, 255, 0),
                        2,
                    )

                    cv2.putText(
                        frame,
                        f"ID {track_id} {confidence:.2f}",
                        (int(x1), max(int(y1) - 10, 0)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 0),
                        2,
                    )

                    cv2.circle(
                        frame,
                        (int(center_x), int(bottom_y)),
                        5,
                        (0, 0, 255),
                        -1,
                    )

            writer.write(frame)
            frame_number += 1

        capture.release()
        writer.release()

        return {
            "output_path": str(output),
            "frame_count": frame_number,
            "tracks": tracks,
        }