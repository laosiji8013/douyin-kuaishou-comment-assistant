import asyncio
import random

from comment_assistant import session


class FakeMouse:
    def __init__(self) -> None:
        self.wheels: list[tuple[int, int]] = []
        self.moves: list[tuple[float, float, int]] = []

    async def wheel(self, x: int, y: int) -> None:
        self.wheels.append((x, y))

    async def move(self, x: float, y: float, *, steps: int) -> None:
        self.moves.append((x, y, steps))


class FakePage:
    def __init__(self) -> None:
        self.viewport_size = {"width": 1280, "height": 800}
        self.mouse = FakeMouse()


class FakeAdapter:
    def __init__(self) -> None:
        self.page = FakePage()


def test_extra_browse_actions_are_executable(monkeypatch) -> None:
    adapter = FakeAdapter()
    sleeps: list[float] = []

    async def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)

    monkeypatch.setattr(session.asyncio, "sleep", fake_sleep)

    async def run_actions() -> None:
        rng = random.Random(42)
        await session.perform_comment_browse_action(adapter, "micro_scroll", rng)
        await session.perform_comment_browse_action(adapter, "settle_cursor", rng)

    asyncio.run(run_actions())

    assert len(adapter.page.mouse.wheels) == 2
    assert adapter.page.mouse.wheels[0][1] > 0
    assert adapter.page.mouse.wheels[1][1] < 0
    assert len(adapter.page.mouse.moves) == 1
    assert len(sleeps) == 2


def test_default_config_exposes_all_browse_actions() -> None:
    from pathlib import Path

    from comment_assistant.config import AppConfig

    root = Path(__file__).resolve().parents[1]
    config = AppConfig.load(root / "config/default.json")

    assert set(config.events["comment_browse_action_weights"]) == {
        "scroll_down",
        "scroll_up",
        "hover_item",
        "wiggle",
        "pause",
        "wander",
        "drift",
        "read_line",
        "micro_scroll",
        "settle_cursor",
    }
