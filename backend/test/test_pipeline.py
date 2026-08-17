from app.services.pipeline import (
    create_pipeline_state,
    get_stage_status,
    invalidate_stage_and_downstream,
    mark_stage_failed,
    should_run_stage,
    update_stage_status,
)


def test_create_pipeline_state():
    state = create_pipeline_state(
        "job_001"
    )

    assert state["job_id"] == "job_001"

    assert (
        get_stage_status(
            state,
            "tracking",
        )
        == "pending"
    )


def test_completed_stage_does_not_run_again():
    state = create_pipeline_state(
        "job_001"
    )

    state = update_stage_status(
        state,
        "tracking",
        "completed",
    )

    assert (
        should_run_stage(
            state,
            "tracking",
        )
        is False
    )


def test_failed_stage_can_run_again():
    state = create_pipeline_state(
        "job_001"
    )

    state = mark_stage_failed(
        state,
        "summary",
        "API unavailable",
    )

    assert (
        should_run_stage(
            state,
            "summary",
        )
        is True
    )


def test_calibration_change_only_invalidates_downstream():
    state = create_pipeline_state(
        "job_001"
    )

    completed_stages = [
        "preprocessing",
        "detection",
        "tracking",
        "calibration",
        "mapping",
        "analytics",
        "summary",
    ]

    for stage in completed_stages:
        state = update_stage_status(
            state,
            stage,
            "completed",
        )

    state = invalidate_stage_and_downstream(
        state,
        "calibration",
    )

    assert (
        get_stage_status(
            state,
            "preprocessing",
        )
        == "completed"
    )

    assert (
        get_stage_status(
            state,
            "detection",
        )
        == "completed"
    )

    assert (
        get_stage_status(
            state,
            "tracking",
        )
        == "completed"
    )

    assert (
        get_stage_status(
            state,
            "calibration",
        )
        == "pending"
    )

    assert (
        get_stage_status(
            state,
            "mapping",
        )
        == "pending"
    )

    assert (
        get_stage_status(
            state,
            "analytics",
        )
        == "pending"
    )

    assert (
        get_stage_status(
            state,
            "summary",
        )
        == "pending"
    )