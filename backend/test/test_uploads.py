import pytest

from app.services.uploads import (
    create_video_id,
    validate_video_filename,
)


def test_valid_video_extension():
    validate_video_filename(
        "game.mp4"
    )


def test_invalid_video_extension():
    with pytest.raises(
        ValueError
    ):
        validate_video_filename(
            "malware.exe"
        )


def test_video_id_is_created():
    video_id = create_video_id()

    assert isinstance(
        video_id,
        str,
    )

    assert len(
        video_id
    ) > 10