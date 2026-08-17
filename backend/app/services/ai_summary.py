import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel


load_dotenv()


class PossessionSummary(BaseModel):
    summary: str
    positive: str
    improvement: str
    evidence_keys: list[str]


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.chatanywhere.org/v1",
)


ALLOWED_EVIDENCE_KEYS = {
    "duration_seconds",
    "result",
    "pass_count",
    "average_spacing_feet",
    "minimum_spacing_feet",
    "maximum_spacing_feet",
}


def validate_evidence_keys(
    evidence_keys: list[str],
) -> None:
    invalid_keys = [
        key
        for key in evidence_keys
        if key not in ALLOWED_EVIDENCE_KEYS
    ]

    if invalid_keys:
        raise ValueError(
            f"Unsupported evidence keys: {invalid_keys}"
        )


def generate_possession_summary(
    possession_analysis: dict,
) -> PossessionSummary:
    facts = {
        "possession_id": possession_analysis[
            "possession_id"
        ],
        "team": possession_analysis["team"],
        "duration_seconds": possession_analysis[
            "duration_seconds"
        ],
        "result": possession_analysis["result"],
        "pass_count": possession_analysis[
            "pass_count"
        ],
        "average_spacing_feet": possession_analysis[
            "spacing"
        ]["average_spacing_feet"],
        "minimum_spacing_feet": possession_analysis[
            "spacing"
        ]["minimum_spacing_feet"],
        "maximum_spacing_feet": possession_analysis[
            "spacing"
        ]["maximum_spacing_feet"],
    }

    response = client.responses.parse(
        model="gpt-5.6",
        input=[
            {
                "role": "system",
                "content": (
                    "You are CourtVision's basketball analysis "
                    "assistant. Explain only the facts provided. "
                    "Do not invent player actions, defensive "
                    "rotations, open shots, drives, passes, or "
                    "events that are not explicitly present. "
                    "Use evidence_keys only from the factual "
                    "fields provided."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(facts),
            },
        ],
        text_format=PossessionSummary,
    )

    summary = response.output_parsed

    validate_evidence_keys(
        summary.evidence_keys
    )

    return summary


def create_fallback_summary(
    possession_analysis: dict,
) -> PossessionSummary:
    spacing = possession_analysis["spacing"]

    return PossessionSummary(
        summary=(
            f"{possession_analysis['team']} had a "
            f"{possession_analysis['duration_seconds']}-second "
            f"possession ending in "
            f"{possession_analysis['result']}."
        ),
        positive=(
            f"Average offensive spacing was "
            f"{spacing['average_spacing_feet']} feet."
        ),
        improvement=(
            f"Minimum spacing reached "
            f"{spacing['minimum_spacing_feet']} feet."
        ),
        evidence_keys=[
            "duration_seconds",
            "result",
            "average_spacing_feet",
            "minimum_spacing_feet",
        ],
    )


def generate_possession_summary(
    possession_analysis: dict,
) -> PossessionSummary:
    facts = {
        "possession_id": possession_analysis[
            "possession_id"
        ],
        "team": possession_analysis["team"],
        "duration_seconds": possession_analysis[
            "duration_seconds"
        ],
        "result": possession_analysis["result"],
        "pass_count": possession_analysis[
            "pass_count"
        ],
        "average_spacing_feet": possession_analysis[
            "spacing"
        ]["average_spacing_feet"],
        "minimum_spacing_feet": possession_analysis[
            "spacing"
        ]["minimum_spacing_feet"],
        "maximum_spacing_feet": possession_analysis[
            "spacing"
        ]["maximum_spacing_feet"],
    }

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are CourtVision's basketball analysis assistant. "
                    "Explain only facts provided by the user. "
                    "Do not invent player actions, defensive rotations, "
                    "open shots, drives, passes, or events. "
                    "Return ONLY valid JSON with exactly these fields: "
                    "summary, positive, improvement, evidence_keys. "
                    "The evidence_keys field must be a JSON array. "
                    "Only use evidence keys from this exact list: "
                    "duration_seconds, result, pass_count, "
                    "average_spacing_feet, minimum_spacing_feet, "
                    "maximum_spacing_feet. "
                    "Do NOT include possession_id or team in evidence_keys."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(facts),
            },
        ],
        response_format={
            "type": "json_object",
        },
    )

    content = response.choices[0].message.content

    if content is None:
        raise ValueError(
            "AI returned an empty response."
        )

    parsed = json.loads(content)

    summary = PossessionSummary(
        **parsed
    )

    validate_evidence_keys(
        summary.evidence_keys
    )

    return summary


def possession_summary_to_dict(
    summary: PossessionSummary,
) -> dict:
    return summary.model_dump()