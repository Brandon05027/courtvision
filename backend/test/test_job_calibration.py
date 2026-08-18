from app.services.calibration import (
    calculate_homography,
    transform_point,
)


def test_four_point_calibration():
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

    mapped = transform_point(
        [50, 50],
        matrix,
    )

    assert mapped is not None

    assert (
        20
        < mapped[0]
        < 30
    )

    assert (
        20
        < mapped[1]
        < 27
    )