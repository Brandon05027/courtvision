from copy import deepcopy


PIPELINE_STAGES = [
    "preprocessing",
    "detection",
    "tracking",
    "calibration",
    "mapping",
    "analytics",
    "summary",
]


VALID_STAGE_STATUSES = {
    "pending",
    "running",
    "completed",
    "failed",
}


def create_pipeline_state(
    job_id: str,
) -> dict:
    return {
        "job_id": job_id,
        "stages": {
            stage: {
                "status": "pending",
                "error": None,
            }
            for stage in PIPELINE_STAGES
        },
    }


def update_stage_status(
    pipeline_state: dict,
    stage: str,
    status: str,
    error: str | None = None,
) -> dict:
    if stage not in PIPELINE_STAGES:
        raise ValueError(
            f"Unknown pipeline stage: {stage}"
        )

    if status not in VALID_STAGE_STATUSES:
        raise ValueError(
            f"Invalid stage status: {status}"
        )

    updated = deepcopy(
        pipeline_state
    )

    updated["stages"][stage] = {
        "status": status,
        "error": error,
    }

    return updated


def get_stage_status(
    pipeline_state: dict,
    stage: str,
) -> str:
    if stage not in PIPELINE_STAGES:
        raise ValueError(
            f"Unknown pipeline stage: {stage}"
        )

    return pipeline_state[
        "stages"
    ][stage]["status"]

def invalidate_stage_and_downstream(
    pipeline_state: dict,
    stage: str,
) -> dict:
    if stage not in PIPELINE_STAGES:
        raise ValueError(
            f"Unknown pipeline stage: {stage}"
        )

    updated = deepcopy(
        pipeline_state
    )

    start_index = PIPELINE_STAGES.index(
        stage
    )

    for downstream_stage in PIPELINE_STAGES[
        start_index:
    ]:
        updated["stages"][
            downstream_stage
        ] = {
            "status": "pending",
            "error": None,
        }

    return updated

def should_run_stage(
    pipeline_state: dict,
    stage: str,
) -> bool:
    status = get_stage_status(
        pipeline_state,
        stage,
    )

    return status in {
        "pending",
        "failed",
    }
def mark_stage_failed(
    pipeline_state: dict,
    stage: str,
    error: Exception | str,
) -> dict:
    return update_stage_status(
        pipeline_state,
        stage,
        "failed",
        error=str(error),
    )
