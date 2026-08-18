from pathlib import Path

from app.services.processing_results import (
    get_movement_heatmap_path,
)

from app.services.visualization import (
    filter_large_position_jumps,
    save_job_movement_heatmap,
    save_player_heatmap,
    save_player_movement_path,
    save_shot_chart,
)


def test_save_shot_chart(tmp_path):
    shots = [
        {
            "court_position": {
                "x": 25.0,
                "y": 10.0,
            },
            "result": "made",
        },
        {
            "court_position": {
                "x": 40.0,
                "y": 20.0,
            },
            "result": "missed",
        },
    ]

    output = (
        tmp_path /
        "shot_chart.png"
    )

    result = save_shot_chart(
        shots,
        str(output),
    )

    assert Path(result).exists()


def test_filter_large_position_jumps():
    tracks = [
        {
            "court_position": {
                "x": 10.0,
                "y": 10.0,
            },
        },
        {
            "court_position": {
                "x": 11.0,
                "y": 11.0,
            },
        },
        {
            "court_position": {
                "x": 40.0,
                "y": 40.0,
            },
        },
    ]

    filtered = (
        filter_large_position_jumps(
            tracks,
            max_distance_feet=8.0,
        )
    )

    assert len(filtered) == 2


def test_save_player_movement_path(
    tmp_path,
):
    tracks = [
        {
            "court_position": {
                "x": 10.0,
                "y": 10.0,
            },
        },
        {
            "court_position": {
                "x": 15.0,
                "y": 15.0,
            },
        },
    ]

    output = (
        tmp_path /
        "movement.png"
    )

    result = (
        save_player_movement_path(
            tracks,
            str(output),
            player_id=1,
        )
    )

    assert Path(result).exists()


def test_save_player_heatmap(
    tmp_path,
):
    tracks = [
        {
            "court_position": {
                "x": 10.0,
                "y": 10.0,
            },
        },
        {
            "court_position": {
                "x": 15.0,
                "y": 15.0,
            },
        },
    ]

    output = (
        tmp_path /
        "heatmap.png"
    )

    result = (
        save_player_heatmap(
            tracks,
            str(output),
            player_id=1,
        )
    )

    assert Path(result).exists()


def test_get_movement_heatmap_path():
    path = (
        get_movement_heatmap_path(
            "test-job"
        )
    )

    assert isinstance(
        path,
        Path,
    )

    assert (
        path.name
        == "movement_heatmap.png"
    )


def test_save_job_movement_heatmap(
    monkeypatch,
    tmp_path,
):
    fake_tracks = []

    for frame_number in range(20):
        fake_tracks.append(
            {
                "track_id": 1,
                "frame_number":
                    frame_number,
                "inside_court":
                    True,
                "court_position": {
                    "x":
                        10.0
                        + frame_number
                        * 0.5,
                    "y": 15.0,
                },
            }
        )

    output_path = (
        tmp_path /
        "movement_heatmap.png"
    )

    monkeypatch.setattr(
        "app.services.visualization.load_mapped_tracks",
        lambda job_id:
            fake_tracks,
    )

    monkeypatch.setattr(
        "app.services.visualization.get_movement_heatmap_path",
        lambda job_id:
            output_path,
    )

    result = (
        save_job_movement_heatmap(
            "test-job"
        )
    )

    assert (
        result
        == output_path
    )

    assert (
        output_path.exists()
    )

    assert (
        output_path
        .stat()
        .st_size
        > 0
    )