from pydantic import BaseModel


class CalibrationPoint(
    BaseModel
):
    x: float
    y: float


class CourtCalibrationRequest(
    BaseModel
):
    image_points: list[
        CalibrationPoint
    ]


class CourtCalibrationResponse(
    BaseModel
):
    job_id: str
    status: str
    stage: str
    progress: int
    mapped_track_count: int
    inside_court_count: int
    message: str