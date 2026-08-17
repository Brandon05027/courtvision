from app.services.evaluation import (
    build_evaluation_report,
    calculate_average_position_error,
    calculate_detection_precision,
    calculate_detection_recall,
    calculate_identity_switch_rate,
    calculate_position_error,
    calculate_processing_fps,
    calculate_tracking_coverage,
)


def test_detection_precision():
    result = calculate_detection_precision(
        true_positives=8,
        false_positives=2,
    )

    assert result == 0.8


def test_detection_recall():
    result = calculate_detection_recall(
        true_positives=9,
        false_negatives=1,
    )

    assert result == 0.9


def test_tracking_coverage():
    result = calculate_tracking_coverage(
        observed_frames=90,
        expected_frames=100,
    )

    assert result == 0.9


def test_identity_switch_rate():
    result = calculate_identity_switch_rate(
        identity_switches=3,
        tracked_frames=300,
    )

    assert result == 0.01


def test_position_error():
    result = calculate_position_error(
        predicted_position=(10.0, 10.0),
        actual_position=(13.0, 14.0),
    )

    assert result == 5.0


def test_average_position_error():
    pairs = [
        (
            (10.0, 10.0),
            (13.0, 14.0),
        ),
        (
            (5.0, 5.0),
            (5.0, 5.0),
        ),
    ]

    result = calculate_average_position_error(
        pairs
    )

    assert result == 2.5


def test_processing_fps():
    result = calculate_processing_fps(
        processed_frames=300,
        processing_seconds=15.0,
    )

    assert result == 20.0


def test_build_evaluation_report():
    report = build_evaluation_report(
        true_positives=90,
        false_positives=10,
        false_negatives=5,
        identity_switches=4,
        tracked_frames=500,
        observed_frames=450,
        expected_frames=500,
        position_pairs=[
            (
                (10.0, 10.0),
                (11.0, 10.0),
            ),
            (
                (20.0, 20.0),
                (20.0, 22.0),
            ),
        ],
        processed_frames=600,
        processing_seconds=30.0,
    )

    assert report[
        "detection_precision"
    ] == 0.9

    assert report[
        "processing_fps"
    ] == 20.0