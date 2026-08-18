from app.services.job_possessions import (
    calculate_spacing_metrics,
)


def test_calculate_spacing_metrics():
    tracks = [
        {
            "frame_number": 1,
            "court_position": {
                "x": 0.0,
                "y": 0.0,
            },
        },
        {
            "frame_number": 1,
            "court_position": {
                "x": 3.0,
                "y": 4.0,
            },
        },
    ]

    result = calculate_spacing_metrics(
        tracks
    )

    assert (
        result[
            "average_spacing_feet"
        ]
        == 5.0
    )

    assert (
        result[
            "minimum_spacing_feet"
        ]
        == 5.0
    )

    assert (
        result[
            "maximum_spacing_feet"
        ]
        == 5.0
    )