import asyncio
import random
from types import SimpleNamespace

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


class FakeField:
    pass


class FakeButton:
    def __init__(self) -> None:
        self.click_count = 0

    async def click(self) -> None:
        self.click_count += 1


class FakePublishingAdapter:
    def __init__(self) -> None:
        self.field = FakeField()
        self.button = FakeButton()

    async def open_comments(self) -> bool:
        return True

    async def comment_input(self) -> FakeField:
        return self.field

    async def send_button(self) -> FakeButton:
        return self.button


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


def test_live_comment_sends_after_single_candidate_confirmation(monkeypatch) -> None:
    adapter = FakePublishingAdapter()
    prompts: list[str] = []
    typed: list[tuple[FakeField, str]] = []

    def fake_ask(prompt: str) -> str:
        prompts.append(prompt)
        return "s"

    async def fake_sleep(_seconds: float) -> None:
        return None

    async def fake_type(field, text, _events, _rng) -> None:
        typed.append((field, text))

    monkeypatch.setattr(session, "ask", fake_ask)
    monkeypatch.setattr(session.asyncio, "sleep", fake_sleep)
    monkeypatch.setattr(session, "type_with_variation", fake_type)

    plan = SimpleNamespace(cancel_draft=False, read_comments_seconds=0.1)
    timing = {
        "think_before_type_min_seconds": 0.1,
        "think_before_type_max_seconds": 0.1,
        "pre_send_pause_min_seconds": 0.1,
        "pre_send_pause_max_seconds": 0.1,
    }

    result = asyncio.run(
        session.review_comment(
            adapter,
            "示例评论",
            plan,
            timing,
            {"typing_typo_probability": 0},
            random.Random(42),
            dry_run=False,
        )
    )

    assert result is True
    assert len(prompts) == 1
    assert "确认发送" in prompts[0]
    assert typed == [(adapter.field, "示例评论")]
    assert adapter.button.click_count == 1
