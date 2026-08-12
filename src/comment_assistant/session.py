from __future__ import annotations

import asyncio
import random
from collections.abc import Callable
from pathlib import Path
from typing import Any

from playwright.async_api import BrowserContext, Locator, Playwright

from .platforms.base import PlatformAdapter
from .randomizer import RandomPlan, SessionRandomizer


def ask(prompt: str) -> str:
    return input(prompt).strip().lower()


async def open_browser(playwright: Playwright, browser: dict[str, Any]) -> BrowserContext:
    profile = Path(browser["profile_directory"])
    profile.mkdir(parents=True, exist_ok=True)
    return await playwright.chromium.launch_persistent_context(
        str(profile),
        headless=bool(browser["headless"]),
        slow_mo=int(browser["slow_mo_ms"]),
        viewport={
            "width": int(browser["viewport_width"]),
            "height": int(browser["viewport_height"]),
        },
    )


async def random_mouse_wander(page: Any, steps: int, rng: random.Random) -> None:
    viewport = page.viewport_size or {"width": 1280, "height": 800}
    for _ in range(steps):
        await page.mouse.move(
            rng.uniform(viewport["width"] * 0.15, viewport["width"] * 0.85),
            rng.uniform(viewport["height"] * 0.15, viewport["height"] * 0.85),
            steps=rng.randint(2, 5),
        )
        await asyncio.sleep(rng.uniform(0.05, 0.2))


async def perform_comment_browse_action(
    adapter: PlatformAdapter,
    action: str,
    rng: random.Random,
) -> None:
    """Perform one visible browsing action without publishing or reacting."""

    page = adapter.page
    viewport = page.viewport_size or {"width": 1280, "height": 800}
    if action in {"scroll_down", "scroll_up"}:
        distance = rng.randint(80, 240) * (1 if action == "scroll_down" else -1)
        await page.mouse.wheel(0, distance)
    elif action == "hover_item":
        await adapter.open_comments()
        await adapter.hover_visible_comment()
    elif action == "wiggle":
        center_x = viewport["width"] * 0.75
        center_y = viewport["height"] * 0.5
        for _ in range(3):
            await page.mouse.move(
                center_x + rng.uniform(-18, 18),
                center_y + rng.uniform(-18, 18),
                steps=2,
            )
    elif action == "pause":
        await asyncio.sleep(rng.uniform(0.5, 1.5))
    elif action == "wander":
        await random_mouse_wander(page, 2, rng)
    elif action == "drift":
        await random_mouse_wander(page, rng.randint(3, 6), rng)
    elif action == "read_line":
        y = rng.uniform(viewport["height"] * 0.35, viewport["height"] * 0.75)
        await page.mouse.move(viewport["width"] * 0.62, y, steps=2)
        await page.mouse.move(viewport["width"] * 0.88, y, steps=6)
    elif action == "micro_scroll":
        distance = rng.randint(35, 90)
        await page.mouse.wheel(0, distance)
        await asyncio.sleep(rng.uniform(0.2, 0.6))
        await page.mouse.wheel(0, -rng.randint(10, distance))
    elif action == "settle_cursor":
        await page.mouse.move(
            viewport["width"] * rng.uniform(0.58, 0.82),
            viewport["height"] * rng.uniform(0.38, 0.72),
            steps=rng.randint(3, 7),
        )
        await asyncio.sleep(rng.uniform(0.3, 0.9))


async def type_with_variation(
    locator: Locator,
    text: str,
    events: dict[str, Any],
    rng: random.Random,
) -> None:
    await locator.click()
    for character in text:
        if character.isalnum() and rng.random() < events["typing_typo_probability"]:
            typo_letters = tuple("qwertyuiopasdfghjklzxcvbnm")
            await locator.press_sequentially(rng.choice(typo_letters))
            await asyncio.sleep(rng.uniform(0.08, 0.25))
            await locator.press("Backspace")
            await asyncio.sleep(
                rng.uniform(events["backspace_min_ms"], events["backspace_max_ms"]) / 1_000
            )
        await locator.press_sequentially(character, delay=rng.randint(45, 130))


async def wait_and_describe(plan: RandomPlan) -> None:
    print(
        f"[计划] behavior={plan.behavior} | watch={plan.watch_tier} "
        f"{plan.watch_seconds:.2f}s | pace={plan.pace}"
    )
    await asyncio.sleep(plan.watch_seconds)


async def offer_like(adapter: PlatformAdapter, dry_run: bool) -> None:
    choice = ask("本条命中点赞候选。是否点赞？[y/N] ")
    if choice != "y":
        return
    if dry_run:
        print("[dry-run] 已记录点赞选择，未点击平台。")
        return
    button = await adapter.like_button()
    if button:
        await button.click()
        print("[完成] 已按本次人工确认点击点赞。")
    else:
        print("[跳过] 未找到点赞按钮。")


async def review_comment(
    adapter: PlatformAdapter,
    comment: str,
    plan: RandomPlan,
    timing: dict[str, Any],
    events: dict[str, Any],
    rng: random.Random,
    dry_run: bool,
) -> bool:
    print(f"\n[候选评论] {comment}")
    choice = ask("选择：[s]确认发送 [e]编辑后发送 [k]跳过 [q]退出：")
    if choice == "q":
        raise KeyboardInterrupt
    if choice == "k" or choice not in {"s", "e"}:
        return False
    if choice == "e":
        edited = input("输入修改后的评论：").strip()
        if not edited:
            print("[跳过] 修改内容为空。")
            return False
        comment = edited
    if plan.cancel_draft:
        second_choice = ask("本条命中随机取消事件。仍要继续？[y/N] ")
        if second_choice != "y":
            print("[取消] 已按随机事件和人工决定放弃本条。")
            return False
    if dry_run:
        print("[dry-run] 已完成逐条审核，未向平台输入或发送。")
        return True
    if not await adapter.open_comments():
        print("[失败] 未找到评论区入口。")
        return False
    await asyncio.sleep(plan.read_comments_seconds)
    field = await adapter.comment_input()
    if not field:
        print("[失败] 未找到评论输入框。")
        return False
    await asyncio.sleep(
        rng.uniform(
            timing["think_before_type_min_seconds"],
            timing["think_before_type_max_seconds"],
        )
    )
    await type_with_variation(field, comment, events, rng)
    await asyncio.sleep(
        rng.uniform(
            timing["pre_send_pause_min_seconds"], timing["pre_send_pause_max_seconds"]
        )
    )
    button = await adapter.send_button()
    if not button:
        print("[失败] 未找到发送按钮，内容保留在输入框中供手动处理。")
        return False
    await button.click()
    print("[完成] 已发送本条已确认评论。")
    return True


async def run_session(
    adapter_factory: Callable[[Any], PlatformAdapter],
    context: BrowserContext,
    config: Any,
    comments: list[str],
    keyword: str,
    navigation_mode: str,
    max_videos: int,
    dry_run: bool,
    seed: int | None,
) -> None:
    page = context.pages[0] if context.pages else await context.new_page()
    adapter = adapter_factory(page)
    randomizer = SessionRandomizer(config.timing, config.events, seed)
    await adapter.open_home()
    input("请在浏览器中完成登录。准备好后按回车继续……")
    if navigation_mode == "search":
        if not await adapter.search(keyword) or not await adapter.open_first_video():
            raise RuntimeError("自动搜索或打开首条视频失败，请改用 --navigation manual")
    else:
        input("请手动打开第一条准备查看的视频，然后按回车继续……")

    for index in range(max_videos):
        plan = randomizer.build_plan()
        print(f"\n===== 第 {index + 1}/{max_videos} 条 =====")
        await wait_and_describe(plan)
        await perform_comment_browse_action(adapter, plan.comment_browse_action, randomizer.rng)
        if plan.hover_comment:
            await adapter.open_comments()
            await adapter.hover_visible_comment()
        if plan.behavior == "browse_author":
            await adapter.hover_author()
        if plan.wander_mouse:
            await random_mouse_wander(page, config.events["mouse_wander_steps"], randomizer.rng)
        if plan.scroll_page:
            await page.mouse.wheel(0, randomizer.rng.randint(80, 260))
        if plan.offer_like or plan.behavior == "watch_and_offer_like":
            await offer_like(adapter, dry_run)
        if plan.behavior not in {"quick_skip", "watch_and_offer_like"}:
            comment = randomizer.rng.choice(comments)
            await review_comment(
                adapter,
                comment,
                plan,
                config.timing,
                config.events,
                randomizer.rng,
                dry_run,
            )
        rest = randomizer.finish_item()
        if rest is not None:
            print(f"[间歇] 连续处理阈值已到，等待 {rest:.2f}s，并切换节奏。")
            await asyncio.sleep(rest)
        if index + 1 < max_videos:
            if navigation_mode == "manual":
                input("请手动切换到下一条视频，然后按回车继续……")
            elif not await adapter.next_video():
                raise RuntimeError("无法进入下一条视频，请改用 --navigation manual")
