from pydantic import BaseModel


class JobAnalyticsResponse(
    BaseModel
):
    job_id: str
    video_id: str
    unique_track_count: int
    mapped_record_count: int
    inside_court_record_count: int
    player_distances_feet: dict[
        str,
        float,
    ]


class TeamClassificationRequest(
    BaseModel
):
    team_a_reference_id: int
    team_b_reference_id: int


class TeamAssignment(
    BaseModel
):
    team: str
    distance_to_team_a: float
    distance_to_team_b: float


class TeamClassificationResponse(
    BaseModel
):
    assignments: dict[
        str,
        TeamAssignment,
    ]