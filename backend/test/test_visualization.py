from pathlib import Path
from app.services.visualization import save_shot_chart

from app.services.visualization import (
    filter_large_position_jumps,
    save_player_heatmap,
    save_player_movement_path,
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

    output = tmp_path / "shot_chart.png"

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

    filtered = filter_large_position_jumps(
        tracks,
        max_distance_feet=8.0,
    )

    assert len(filtered) == 2

def test_save_player_movement_path(tmp_path):
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

    output = tmp_path / "movement.png"

    result = save_player_movement_path(
        tracks,
        str(output),
        player_id=1,
    )

    assert Path(result).exists()

def test_save_player_heatmap(tmp_path):
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

    output = tmp_path / "heatmap.png"

    result = save_player_heatmap(
        tracks,
        str(output),
        player_id=1,
    )

    assert Path(result).exists()