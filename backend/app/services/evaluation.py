import math


def calculate_detection_precision(
    true_positives: int,
    false_positives: int,
) -> float:
    denominator = (
        true_positives
        + false_positives
    )

    if denominator == 0:
        return 0.0

    return true_positives / denominator


def calculate_detection_recall(
    true_positives: int,
    false_negatives: int,
) -> float:
    denominator = (
        true_positives
        + false_negatives
    )

    if denominator == 0:
        return 0.0

    return true_positives / denominator


def calculate_labeled_tracking_coverage(
    observed_frames: int,
    expected_frames: int,
) -> float:
    if expected_frames <= 0:
        raise ValueError(
            "expected_frames must be greater than 0."
        )

    coverage = (
        observed_frames
        / expected_frames
    )

    return min(
        coverage,
        1.0,
    )


def calculate_identity_switch_rate(
    identity_switches: int,
    tracked_frames: int,
) -> float:
    if tracked_frames <= 0:
        return 0.0

    return (
        identity_switches
        / tracked_frames
    )


def calculate_position_error(
    predicted_position: tuple[float, float],
    actual_position: tuple[float, float],
) -> float:
    dx = (
        predicted_position[0]
        - actual_position[0]
    )

    dy = (
        predicted_position[1]
        - actual_position[1]
    )

    return math.hypot(
        dx,
        dy,
    )


def calculate_average_position_error(
    position_pairs: list[
        tuple[
            tuple[float, float],
            tuple[float, float],
        ]
    ],
) -> float:
    if not position_pairs:
        return 0.0

    errors = [
        calculate_position_error(
            predicted,
            actual,
        )
        for predicted, actual
        in position_pairs
    ]

    return (
        sum(errors)
        / len(errors)
    )


def calculate_processing_fps(
    processed_frames: int,
    processing_seconds: float,
) -> float:
    if processing_seconds <= 0:
        raise ValueError(
            "processing_seconds must be greater than 0."
        )

    return (
        processed_frames
        / processing_seconds
    )


def build_evaluation_report(
    true_positives: int,
    false_positives: int,
    false_negatives: int,
    identity_switches: int,
    tracked_frames: int,
    observed_frames: int,
    expected_frames: int,
    position_pairs: list[
        tuple[
            tuple[float, float],
            tuple[float, float],
        ]
    ],
    processed_frames: int,
    processing_seconds: float,
) -> dict:
    return {
        "detection_precision": round(
            calculate_detection_precision(
                true_positives,
                false_positives,
            ),
            4,
        ),
        "detection_recall": round(
            calculate_detection_recall(
                true_positives,
                false_negatives,
            ),
            4,
        ),
        "tracking_coverage": round(
            calculate_labeled_tracking_coverage(
                observed_frames,
                expected_frames,
            ),
            4,
        ),
        "identity_switch_rate": round(
            calculate_identity_switch_rate(
                identity_switches,
                tracked_frames,
            ),
            4,
        ),
        "average_position_error_feet": round(
            calculate_average_position_error(
                position_pairs
            ),
            2,
        ),
        "processing_fps": round(
            calculate_processing_fps(
                processed_frames,
                processing_seconds,
            ),
            2,
        ),
    }