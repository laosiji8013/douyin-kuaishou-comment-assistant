from pathlib import Path

from comment_assistant.config import AppConfig
from comment_assistant.randomizer import SessionRandomizer

ROOT = Path(__file__).resolve().parents[1]


def test_seed_reproduces_random_plans() -> None:
    config = AppConfig.load(ROOT / "config/default.json")
    first = SessionRandomizer(config.timing, config.events, seed=42)
    second = SessionRandomizer(config.timing, config.events, seed=42)

    assert first.build_plan() == second.build_plan()
    assert first.finish_item() == second.finish_item()


def test_plan_values_stay_in_expected_domains() -> None:
    config = AppConfig.load(ROOT / "config/default.json")
    randomizer = SessionRandomizer(config.timing, config.events, seed=7)

    plans = [randomizer.build_plan() for _ in range(50)]

    assert {plan.pace for plan in plans} <= set(config.timing["pace_weights"])
    assert {plan.behavior for plan in plans} <= set(config.events["behavior_weights"])
    assert {plan.comment_browse_action for plan in plans} <= set(
        config.events["comment_browse_action_weights"]
    )
    assert all(plan.watch_seconds >= 0 for plan in plans)
    assert all(plan.watch_tier == "skip" for plan in plans if plan.behavior == "quick_skip")
    assert all(plan.watch_tier == "deep" for plan in plans if plan.behavior == "deep_engage")
