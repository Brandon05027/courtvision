import cv2
import numpy as np


def calculate_homography(
    image_points: list[list[float]],
    court_points: list[list[float]],
) -> np.ndarray: #give 4 point from the video and 4 matching points on the basketball court
    if len(image_points) != 4:
        raise ValueError("Exactly 4 image points are required.")

    if len(court_points) != 4:
        raise ValueError("Exactly 4 court points are required.")

    source = np.array(image_points, dtype=np.float32)
    destination = np.array(court_points, dtype=np.float32)

    matrix = cv2.getPerspectiveTransform(
        source,
        destination,
    )

    return matrix

def transform_point(
    point: tuple[float, float],
    homography_matrix: np.ndarray,
) -> tuple[float, float]:
    points = np.array(
        [[[point[0], point[1]]]],
        dtype=np.float32,
    )

    transformed = cv2.perspectiveTransform(
        points,
        homography_matrix,
    )

    x = float(transformed[0][0][0])
    y = float(transformed[0][0][1])

    return round(x, 2), round(y, 2)