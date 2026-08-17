from fastapi import APIRouter

from app.schemas.possession import (
    PossessionAnalysisInput,
    PossessionSummaryResponse,
)
from app.services.ai_summary import (
    generate_possession_summary_safe,
)


router = APIRouter(
    prefix="/api/v1/possessions",
    tags=["possessions"],
)


@router.post(
    "/summary",
    response_model=PossessionSummaryResponse,
)
def create_possession_summary(
    possession: PossessionAnalysisInput,
) -> PossessionSummaryResponse:
    analysis = possession.model_dump()

    summary = generate_possession_summary_safe(
        analysis
    )

    return PossessionSummaryResponse(
        **summary.model_dump()
    )