import json
from pathlib import Path

import pytest

from comment_assistant.config import AppConfig

ROOT = Path(__file__).resolve().parents[1]


def test_default_config_is_valid() -> None:
    config = AppConfig.load(ROOT / "config/default.json")
    assert config.events["mouse_wander_probability"] == 0.30
    assert config.session["default_max_videos"] == 20


def test_packaged_default_matches_repository_default() -> None:
    packaged = ROOT / "src/comment_assistant/resources/default.json"
    assert json.loads(packaged.read_text(encoding="utf-8")) == json.loads(
        (ROOT / "config/default.json").read_text(encoding="utf-8")
    )


@pytest.mark.parametrize("name", ["comments.example.json", "keywords.example.json"])
def test_packaged_examples_match_repository_examples(name: str) -> None:
    packaged = ROOT / "src/comment_assistant/resources" / name
    assert json.loads(packaged.read_text(encoding="utf-8")) == json.loads(
        (ROOT / "data" / name).read_text(encoding="utf-8")
    )


def test_invalid_probability_is_rejected(tmp_path: Path) -> None:
    source = json.loads((ROOT / "config/default.json").read_text(encoding="utf-8"))
    source["events"]["cancel_draft_probability"] = 1.1
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(source), encoding="utf-8")

    with pytest.raises(ValueError, match="between 0 and 1"):
        AppConfig.load(path)


def test_invalid_range_is_rejected(tmp_path: Path) -> None:
    source = json.loads((ROOT / "config/default.json").read_text(encoding="utf-8"))
    source["timing"]["read_comments_min_seconds"] = 9
    source["timing"]["read_comments_max_seconds"] = 2
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(source), encoding="utf-8")

    with pytest.raises(ValueError, match="cannot exceed"):
        AppConfig.load(path)
