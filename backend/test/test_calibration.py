import numpy as np
import pytest

from app.services.calibration import (
    calculate_homography,
    transform_point,
)


def test_calculate_homography_requires_four_points():
    image_points = [
        [0, 0],
        [100, 0],
        [100, 100],
    ]

    court_points = [
        [0, 0],
        [50, 0],
        [50, 47],
    ]

    with pytest.raises(ValueError):
        calculate_homography(
            image_points,
            court_points,
        )


def test_homography_maps_known_points():
    image_points = [
        [0, 0],
        [100, 0],
        [100, 100],
        [0, 100],
    ]

    court_points = [
        [0, 0],
        [50, 0],
        [50, 47],
        [0, 47],
    ]

    matrix = calculate_homography(
        image_points,
        court_points,
    )

    transformed = transform_point(
        (100, 100),
        matrix,
    )

    assert transformed[0] == pytest.approx(
        50,
        abs=0.01,
    )

    assert transformed[1] == pytest.approx(
        47,
        abs=0.01,
    )