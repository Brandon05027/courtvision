from pydantic import BaseModel#The api will check the request, not random data
from pydantic import BaseModel

class SpacingInput(BaseModel):
    average_spacing_feet: float
    minimum_spacing_feet: float
    maximum_spacing_feet: float
    spacing_sample_count: int


class PossessionAnalysisInput(BaseModel):
    possession_id: str
    team: str
    start_time: float
    end_time: float
    duration_seconds: float
    result: str
    pass_count: int
    manually_segmented: bool
    spacing: SpacingInput


class PossessionSummaryResponse(BaseModel):
    summary: str
    positive: str
    improvement: str
    evidence_keys: list[str]

class PossessionReviewRequest(BaseModel):
    start_time: float
    end_time: float
    result: str
    pass_count: int = 0


class PossessionReviewResponse(BaseModel):
    possession_id: str
    start_time: float
    end_time: float
    duration_seconds: float
    result: str
    pass_count: int
    average_spacing_feet: float | None
    minimum_spacing_feet: float | None
    maximum_spacing_feet: float | None