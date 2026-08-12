from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any


def weighted_choice(rng: random.Random, values: dict[str, float]) -> str:
    total = sum(values.values())
    point = rng.random() * total
    cumulative = 0.0
    for name, weight in values.items():
        cumulative += weight
        if point <= cumulative:
            return name
    return next(reversed(values))


@dataclass(slots=True)
class RandomPlan:
    behavior: str
    comment_browse_action: str
    watch_tier: str
    watch_seconds: float
    pace: str
    pace_multiplier: float
    read_comments_seconds: float
    wander_mouse: bool
    hover_comment: bool
    scroll_page: bool
    cancel_draft: bool
    offer_like: bool


class SessionRandomizer:
    def __init__(self, timing: dict[str, Any], events: dict[str, Any], seed: int | None):
        self.timing = timing
        self.events = events
        self.rng = random.Random(seed)
        self.current_pace = "normal"
        self.items_in_burst = 0
        self._skip_window: list[bool] = []

    def _choose_watch(self, forced_tier: str | None = None) -> tuple[str, float]:
        weights = {tier["name"]: float(tier["weight"]) for tier in self.timing["watch_tiers"]}
        name = forced_tier or weighted_choice(self.rng, weights)
        tier = next(item for item in self.timing["watch_tiers"] if item["name"] == name)
        seconds = self.rng.uniform(tier["min_seconds"], tier["max_seconds"])
        if name == "deep" and self.rng.random() < self.timing["deep_extra_probability"]:
            seconds += self.rng.uniform(
                self.timing["deep_extra_min_seconds"],
                self.timing["deep_extra_max_seconds"],
            )
        return name, seconds * self.timing["pace_multipliers"][self.current_pace]

    def _refill_skip_window(self) -> None:
        total = self.rng.randint(self.events["skip_window_min"], self.events["skip_window_max"])
        skip_count = self.rng.randint(
            self.events["skip_per_window_min"], self.events["skip_per_window_max"]
        )
        skip_indexes = set(self.rng.sample(range(total), min(skip_count, total)))
        self._skip_window = [index in skip_indexes for index in range(total)]

    def should_skip_comment(self) -> bool:
        if not self._skip_window:
            self._refill_skip_window()
        return self._skip_window.pop(0)

    def build_plan(self) -> RandomPlan:
        behavior = weighted_choice(self.rng, self.events["behavior_weights"])
        forced_tiers = {"quick_skip": "skip", "deep_engage": "deep"}
        watch_tier, watch_seconds = self._choose_watch(forced_tiers.get(behavior))
        if self.should_skip_comment() and behavior == "watch_and_prepare_comment":
            behavior = "quick_skip"
        return RandomPlan(
            behavior=behavior,
            comment_browse_action=weighted_choice(
                self.rng, self.events["comment_browse_action_weights"]
            ),
            watch_tier=watch_tier,
            watch_seconds=round(watch_seconds, 2),
            pace=self.current_pace,
            pace_multiplier=float(self.timing["pace_multipliers"][self.current_pace]),
            read_comments_seconds=round(
                self.rng.uniform(
                    self.timing["read_comments_min_seconds"],
                    self.timing["read_comments_max_seconds"],
                )
                * self.timing["pace_multipliers"][self.current_pace],
                2,
            ),
            wander_mouse=self.rng.random() < self.events["mouse_wander_probability"],
            hover_comment=self.rng.random() < self.events["hover_comment_probability"],
            scroll_page=self.rng.random() < self.events["page_scroll_probability"],
            cancel_draft=self.rng.random() < self.events["cancel_draft_probability"],
            offer_like=self.rng.random() < self.events["like_offer_probability"],
        )

    def finish_item(self) -> float | None:
        self.items_in_burst += 1
        threshold = self.rng.randint(
            self.timing["burst_count_min"], self.timing["burst_count_max"]
        )
        if self.items_in_burst < threshold:
            return None
        self.items_in_burst = 0
        self.current_pace = weighted_choice(self.rng, self.timing["pace_weights"])
        return round(
            self.rng.uniform(
                self.timing["burst_rest_min_seconds"],
                self.timing["burst_rest_max_seconds"],
            ),
            2,
        )
