from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _number(value: Any, path: str, minimum: float = 0.0) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{path} must be a number")
    if value < minimum:
        raise ValueError(f"{path} must be >= {minimum}")
    return float(value)


def _integer(value: Any, path: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{path} must be an integer")
    if value < minimum:
        raise ValueError(f"{path} must be >= {minimum}")
    return value


def _range(data: dict[str, Any], minimum_key: str, maximum_key: str, prefix: str) -> None:
    minimum = _number(data[minimum_key], f"{prefix}.{minimum_key}")
    maximum = _number(data[maximum_key], f"{prefix}.{maximum_key}")
    if minimum > maximum:
        raise ValueError(f"{prefix}: {minimum_key} cannot exceed {maximum_key}")


def _weights(values: dict[str, Any], path: str) -> dict[str, float]:
    if not values:
        raise ValueError(f"{path} cannot be empty")
    result = {key: _number(value, f"{path}.{key}") for key, value in values.items()}
    total = sum(result.values())
    if total <= 0:
        raise ValueError(f"{path} must contain at least one positive weight")
    return result


@dataclass(frozen=True, slots=True)
class AppConfig:
    browser: dict[str, Any]
    timing: dict[str, Any]
    events: dict[str, Any]
    session: dict[str, Any]

    @classmethod
    def load(cls, path: Path) -> AppConfig:
        with path.open("r", encoding="utf-8") as source:
            data = json.load(source)
        required = ("browser", "timing", "events", "session")
        missing = [key for key in required if not isinstance(data.get(key), dict)]
        if missing:
            raise ValueError(f"missing object sections: {', '.join(missing)}")
        config = cls(**{key: data[key] for key in required})
        config.validate()
        return config

    def validate(self) -> None:
        _integer(self.browser["viewport_width"], "browser.viewport_width", 320)
        _integer(self.browser["viewport_height"], "browser.viewport_height", 240)
        _integer(self.browser["slow_mo_ms"], "browser.slow_mo_ms")

        tiers = self.timing.get("watch_tiers")
        if not isinstance(tiers, list) or not tiers:
            raise ValueError("timing.watch_tiers must be a non-empty list")
        names: set[str] = set()
        total = 0.0
        for index, tier in enumerate(tiers):
            prefix = f"timing.watch_tiers[{index}]"
            if not isinstance(tier, dict) or not str(tier.get("name", "")).strip():
                raise ValueError(f"{prefix}.name is required")
            name = str(tier["name"])
            if name in names:
                raise ValueError(f"duplicate watch tier: {name}")
            names.add(name)
            minimum = _number(tier["min_seconds"], f"{prefix}.min_seconds")
            maximum = _number(tier["max_seconds"], f"{prefix}.max_seconds")
            if minimum > maximum:
                raise ValueError(f"{prefix}.min_seconds cannot exceed max_seconds")
            total += _number(tier["weight"], f"{prefix}.weight")
        if total <= 0:
            raise ValueError("timing.watch_tiers needs a positive total weight")

        for key in (
            "deep_extra_probability",
            "hover_comment_probability",
            "mouse_wander_probability",
            "page_scroll_probability",
            "typing_typo_probability",
            "cancel_draft_probability",
            "like_offer_probability",
        ):
            section = self.timing if key == "deep_extra_probability" else self.events
            value = _number(section[key], f"{'timing' if section is self.timing else 'events'}.{key}")
            if value > 1:
                raise ValueError(f"{key} must be between 0 and 1")

        for keys in (
            ("deep_extra_min_seconds", "deep_extra_max_seconds"),
            ("read_comments_min_seconds", "read_comments_max_seconds"),
            ("think_before_type_min_seconds", "think_before_type_max_seconds"),
            ("pre_send_pause_min_seconds", "pre_send_pause_max_seconds"),
            ("burst_rest_min_seconds", "burst_rest_max_seconds"),
        ):
            _range(self.timing, keys[0], keys[1], "timing")
        _range(self.events, "backspace_min_ms", "backspace_max_ms", "events")

        _weights(self.timing["pace_multipliers"], "timing.pace_multipliers")
        pace_weights = _weights(self.timing["pace_weights"], "timing.pace_weights")
        if set(pace_weights) != set(self.timing["pace_multipliers"]):
            raise ValueError("pace_weights and pace_multipliers must use the same names")
        _weights(self.events["behavior_weights"], "events.behavior_weights")
        _weights(
            self.events["comment_browse_action_weights"],
            "events.comment_browse_action_weights",
        )

        for prefix, data, minimum_key, maximum_key in (
            ("timing", self.timing, "burst_count_min", "burst_count_max"),
            ("events", self.events, "skip_window_min", "skip_window_max"),
            ("events", self.events, "skip_per_window_min", "skip_per_window_max"),
        ):
            minimum = _integer(data[minimum_key], f"{prefix}.{minimum_key}")
            maximum = _integer(data[maximum_key], f"{prefix}.{maximum_key}")
            if minimum > maximum:
                raise ValueError(f"{prefix}.{minimum_key} cannot exceed {maximum_key}")
        if self.events["skip_per_window_max"] > self.events["skip_window_max"]:
            raise ValueError("skip_per_window_max cannot exceed skip_window_max")


def load_string_list(path: Path, label: str) -> list[str]:
    with path.open("r", encoding="utf-8") as source:
        values = json.load(source)
    if not isinstance(values, list):
        raise TypeError(f"{label} must be a JSON array")
    result = [str(value).strip() for value in values if str(value).strip()]
    if not result:
        raise ValueError(f"{label} cannot be empty")
    return result
