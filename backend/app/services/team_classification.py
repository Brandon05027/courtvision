import cv2
import numpy as np


def crop_torso(
    frame: np.ndarray,
    bounding_box: dict,
) -> np.ndarray:
    """
    Crop the center-upper portion of a person's bounding box.

    This area is more likely to contain the jersey while avoiding
    skin, shorts, shoes, and background pixels.
    """
    x1 = int(bounding_box["x1"])
    y1 = int(bounding_box["y1"])
    x2 = int(bounding_box["x2"])
    y2 = int(bounding_box["y2"])

    width = x2 - x1
    height = y2 - y1

    torso_x1 = x1 + int(width * 0.25)
    torso_x2 = x2 - int(width * 0.25)

    torso_y1 = y1 + int(height * 0.20)
    torso_y2 = y1 + int(height * 0.50)

    return frame[
        torso_y1:torso_y2,
        torso_x1:torso_x2,
    ]


def extract_jersey_color(
    image: np.ndarray,
) -> tuple[float, float, float]:
    """
    Convert a jersey crop to LAB color space and return its
    median color.

    LAB separates lightness from color information and is more
    useful for comparing jersey appearance than raw BGR pixels.
    """
    if image.size == 0:
        raise ValueError("Image crop is empty.")

    lab_image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2LAB,
    )

    pixels = lab_image.reshape(-1, 3)

    median_color = np.median(
        pixels,
        axis=0,
    )

    return (
        float(median_color[0]),
        float(median_color[1]),
        float(median_color[2]),
    )


def collect_track_jersey_colors(
    video_path: str,
    tracks: list[dict],
    sample_every_n_frames: int = 5,
    start_frame: int = 0,
    end_frame: int | None = None,
) -> dict[int, list[tuple[float, float, float]]]:
    """
    Collect multiple jersey-color samples for every tracked person.

    Using multiple frames makes team classification more stable than
    trying to classify a player from a single image.
    """
    capture = cv2.VideoCapture(video_path)

    if not capture.isOpened():
        capture.release()
        raise ValueError(
            f"Could not open video: {video_path}"
        )

    tracks_by_frame: dict[int, list[dict]] = {}

    for track in tracks:
        if not track.get("inside_court", True):
            continue

        frame_number = track["frame_number"]

        if frame_number < start_frame:
            continue

        if (
            end_frame is not None
            and frame_number > end_frame
        ):
            continue

        if frame_number % sample_every_n_frames != 0:
            continue

        tracks_by_frame.setdefault(
            frame_number,
            [],
        ).append(track)

    colors_by_track: dict[
        int,
        list[tuple[float, float, float]],
    ] = {}

    frame_number = 0

    while True:
        success, frame = capture.read()

        if not success:
            break

        if (
            end_frame is not None
            and frame_number > end_frame
        ):
            break

        frame_tracks = tracks_by_frame.get(
            frame_number,
            [],
        )

        for track in frame_tracks:
            torso = crop_torso(
                frame,
                track["bounding_box"],
            )

            if torso.size == 0:
                continue

            jersey_color = extract_jersey_color(
                torso
            )

            track_id = track["track_id"]

            colors_by_track.setdefault(
                track_id,
                [],
            ).append(jersey_color)

        frame_number += 1

    capture.release()

    return colors_by_track


def calculate_track_color_profiles(
    colors_by_track: dict[
        int,
        list[tuple[float, float, float]],
    ],
    minimum_samples: int = 3,
) -> dict[int, tuple[float, float, float]]:
    """
    Reduce many jersey samples into one representative LAB color
    for each Track ID.
    """
    profiles: dict[
        int,
        tuple[float, float, float],
    ] = {}

    for track_id, colors in colors_by_track.items():
        if len(colors) < minimum_samples:
            continue

        color_array = np.array(
            colors,
            dtype=np.float32,
        )

        median_color = np.median(
            color_array,
            axis=0,
        )

        profiles[track_id] = (
            float(median_color[0]),
            float(median_color[1]),
            float(median_color[2]),
        )

    return profiles


def classify_track_teams(
    profiles: dict[
        int,
        tuple[float, float, float],
    ],
    team_a_reference_id: int,
    team_b_reference_id: int,
    unknown_distance_threshold: float = 30.0,
) -> dict[int, dict]:
    """
    Classify each Track ID by comparing its representative jersey
    color with one confirmed player from Team A and Team B.

    Tracks that are not sufficiently similar to either team are
    classified as unknown.
    """
    if team_a_reference_id not in profiles:
        raise ValueError(
            "Team A reference ID has no color profile."
        )

    if team_b_reference_id not in profiles:
        raise ValueError(
            "Team B reference ID has no color profile."
        )

    team_a_color = np.array(
        profiles[team_a_reference_id],
        dtype=np.float32,
    )

    team_b_color = np.array(
        profiles[team_b_reference_id],
        dtype=np.float32,
    )

    assignments: dict[int, dict] = {}

    for track_id, color in profiles.items():
        color_vector = np.array(
            color,
            dtype=np.float32,
        )

        distance_to_team_a = float(
            np.linalg.norm(
                color_vector - team_a_color
            )
        )

        distance_to_team_b = float(
            np.linalg.norm(
                color_vector - team_b_color
            )
        )

        nearest_distance = min(
            distance_to_team_a,
            distance_to_team_b,
        )

        if (
            nearest_distance
            > unknown_distance_threshold
        ):
            team = "unknown"

        elif (
            distance_to_team_a
            < distance_to_team_b
        ):
            team = "team_a"

        else:
            team = "team_b"

        assignments[track_id] = {
            "team": team,
            "distance_to_team_a": round(
                distance_to_team_a,
                2,
            ),
            "distance_to_team_b": round(
                distance_to_team_b,
                2,
            ),
            "representative_color": color,
        }

    return assignments