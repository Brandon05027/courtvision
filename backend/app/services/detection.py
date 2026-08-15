from pathlib import Path

import cv2
from ultralytics import YOLO


PERSON_CLASS_ID = 0


class PlayerDetector:
    def __init__(self, model_name: str = "yolo26n.pt"):
        self.model = YOLO(model_name)

    def detect_players(
        self,
        image_path: str,
        confidence_threshold: float = 0.4,
    ) -> list[dict]:
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        results = self.model.predict(
            source=str(path),
            conf=confidence_threshold,
            verbose=False,
        )

        detections = []

        for result in results:
            if result.boxes is None:
                continue

            for box in result.boxes:
                class_id = int(box.cls.item())

                if class_id != PERSON_CLASS_ID:
                    continue

                x1, y1, x2, y2 = box.xyxy[0].tolist()
                confidence = float(box.conf.item())

                center_x = (x1 + x2) / 2
                bottom_y = y2

                detections.append(
                    {
                        "class_id": class_id,
                        "class_name": "person",
                        "confidence": round(confidence, 4),
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

        return detections

    def save_annotated_image(
        self,
        image_path: str,
        output_path: str,
        confidence_threshold: float = 0.4,
    ) -> str:
        detections = self.detect_players(
            image_path,
            confidence_threshold,
        )

        image = cv2.imread(image_path)

        if image is None:
            raise ValueError(f"Could not read image: {image_path}")

        for detection in detections:
            box = detection["bounding_box"]

            x1 = int(box["x1"])
            y1 = int(box["y1"])
            x2 = int(box["x2"])
            y2 = int(box["y2"])

            confidence = detection["confidence"]

            cv2.rectangle(
                image,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2,
            )

            point = detection["court_contact_point"]

            contact_x = int(point["x"])
            contact_y = int(point["y"]) #give approximate court position in the output image.

            cv2.circle(
                image,
                (contact_x, contact_y),
                5,
                (0, 0, 255),
                -1,
            )

            point = detection["court_contact_point"]

            contact_x = int(point["x"])
            contact_y = int(point["y"])

            cv2.circle(
                image,
                (contact_x, contact_y),
                5,
                (0, 0, 255),
                -1,
            )

            cv2.putText(
                image,
                f"player {confidence:.2f}",
                (x1, max(y1 - 10, 0)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        saved = cv2.imwrite(str(output), image)

        if not saved:
            raise ValueError(
                f"Could not save annotated image: {output_path}"
            )

        return str(output)