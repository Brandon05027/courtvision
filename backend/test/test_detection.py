import pytest

from app.services.detection import PlayerDetector

def test_missing_img_is_rejected():
    detector = PlayerDetector.__new__(PlayerDetector) #it only checks validation logic so we dont need to use YOLO model, which we dont need to use PlayerDetector()

    with pytest.raises(FileNotFoundError):
        detector.detect_players("missing-image.jpg")