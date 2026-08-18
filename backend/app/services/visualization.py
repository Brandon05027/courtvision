from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle, Rectangle #it will connect the points of the player's movement tgt


COURT_WIDTH = 50.0
COURT_LENGTH = 47.0

from app.services.processing_results import (
    get_movement_heatmap_path,
    load_mapped_tracks,
)

def save_job_movement_heatmap(
    job_id: str,
):
    mapped_tracks = (
        load_mapped_tracks(
            job_id
        )
    )

    x_positions = []
    y_positions = []

    for record in mapped_tracks:
        if not record.get(
            "inside_court",
            False,
        ):
            continue

        court_position = (
            record.get(
                "court_position"
            )
        )

        if not court_position:
            continue

        x = court_position.get(
            "x"
        )

        y = court_position.get(
            "y"
        )

        if x is None or y is None:
            continue

        x_positions.append(
            float(x)
        )

        y_positions.append(
            float(y)
        )

    if not x_positions:
        raise ValueError(
            "No inside-court movement "
            "positions were available."
        )

    output_path = (
        get_movement_heatmap_path(
            job_id
        )
    )

    figure, axis = (
        plt.subplots(
            figsize=(10, 7)
        )
    )

    heatmap = axis.hist2d(
        x_positions,
        y_positions,
        bins=[
            25,
            24,
        ],
    )

    axis.set_xlim(
        0,
        50,
    )

    axis.set_ylim(
        47,
        0,
    )

    axis.set_xlabel(
        "Court X (feet)"
    )

    axis.set_ylabel(
        "Court Y (feet)"
    )

    axis.set_title(
        "CourtVision Movement Heatmap"
    )

    figure.colorbar(
        heatmap[3],
        ax=axis,
        label="Tracking observations",
    )

    figure.tight_layout()

    figure.savefig(
        output_path,
        dpi=150,
        bbox_inches="tight",
    )

    plt.close(
        figure
    )

    return output_path

def draw_half_court(ax):
    ax.set_xlim(0, COURT_WIDTH)
    ax.set_ylim(COURT_LENGTH, 0)

    ax.set_aspect("equal")

    outer = Rectangle(
        (0, 0),
        COURT_WIDTH,
        COURT_LENGTH,
        fill=False,
    )
    ax.add_patch(outer)

    paint = Rectangle(
        (17, 0),
        16,
        19,
        fill=False,
    )
    ax.add_patch(paint)

    free_throw_circle = Circle(
        (25, 19),
        6,
        fill=False,
    )
    ax.add_patch(free_throw_circle)

    hoop = Circle(
        (25, 5.25),
        0.75,
        fill=False,
    )
    ax.add_patch(hoop)

    backboard = Rectangle(
        (22, 4),
        6,
        0,
        fill=False,
    )
    ax.add_patch(backboard)

    three_point_arc = Arc(
        (25, 5.25),
        47.5,
        47.5,
        theta1=22,
        theta2=158,
    )
    ax.add_patch(three_point_arc)

    ax.set_xlabel("Court width (ft)")
    ax.set_ylabel("Court length (ft)")

def save_player_movement_path(
    player_tracks: list[dict],
    output_path: str,
    player_id: int | None = None,
) -> str:
    if not player_tracks:
        raise ValueError("Player tracks cannot be empty.")

    x_positions = [
        track["court_position"]["x"]
        for track in player_tracks
    ]

    y_positions = [
        track["court_position"]["y"]
        for track in player_tracks
    ]

    figure, ax = plt.subplots(
        figsize=(8, 7),
    )

    draw_half_court(ax)

    ax.plot(
        x_positions,
        y_positions,
        linewidth=1.5,
    )

    ax.scatter(
        x_positions[0],
        y_positions[0],
        s=60,
        label="Start",
    )

    ax.scatter(
        x_positions[-1],
        y_positions[-1],
        s=60,
        label="End",
    )

    title = "Player Movement Path"

    if player_id is not None:
        title += f" — ID {player_id}"

    ax.set_title(title)
    ax.legend()

    output = Path(output_path)
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    figure.savefig(
        output,
        bbox_inches="tight",
    )

    plt.close(figure)

    return str(output)

def save_player_heatmap(
    player_tracks: list[dict],
    output_path: str,
    player_id: int | None = None,
    bins: int = 20,
) -> str:
    if not player_tracks:
        raise ValueError("Player tracks cannot be empty.")

    x_positions = [
        track["court_position"]["x"]
        for track in player_tracks
    ]

    y_positions = [
        track["court_position"]["y"]
        for track in player_tracks
    ]

    figure, ax = plt.subplots(
        figsize=(8, 7),
    )

    draw_half_court(ax)

    heatmap = ax.hist2d(
        x_positions,
        y_positions,
        bins=bins,
        range=[
            [0, COURT_WIDTH],
            [0, COURT_LENGTH],
        ],
        alpha=0.65,
    )

    figure.colorbar(
        heatmap[3],
        ax=ax,
        label="Position frequency",
    )

    title = "Player Position Heatmap"

    if player_id is not None:
        title += f" — ID {player_id}"

    ax.set_title(title)

    output = Path(output_path)

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    figure.savefig(
        output,
        bbox_inches="tight",
    )

    plt.close(figure)

    return str(output)

def filter_large_position_jumps(
    player_tracks: list[dict],
    max_distance_feet: float = 8.0,
) -> list[dict]:
    if len(player_tracks) < 2:
        return player_tracks

    filtered = [player_tracks[0]]

    for track in player_tracks[1:]:
        previous = filtered[-1]

        previous_position = previous["court_position"]
        current_position = track["court_position"]

        dx = (
            current_position["x"]
            - previous_position["x"]
        )

        dy = (
            current_position["y"]
            - previous_position["y"]
        )

        distance = (
            dx ** 2
            + dy ** 2
        ) ** 0.5

        if distance <= max_distance_feet:
            filtered.append(track)

    return filtered

def save_shot_chart(
    shots: list[dict],
    output_path: str,
) -> str:
    if not shots:
        raise ValueError("Shot list cannot be empty.")

    figure, ax = plt.subplots(
        figsize=(8, 7),
    )

    draw_half_court(ax)

    for shot in shots:
        position = shot["court_position"]

        marker = (
            "o"
            if shot["result"] == "made"
            else "x"
        )

        ax.scatter(
            position["x"],
            position["y"],
            marker=marker,
            s=80,
        )

    ax.set_title("CourtVision Shot Chart")

    output = Path(output_path)

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    figure.savefig(
        output,
        bbox_inches="tight",
    )

    plt.close(figure)

    return str(output)