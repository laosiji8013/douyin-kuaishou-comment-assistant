from __future__ import annotations

from playwright.async_api import Locator

from .base import PlatformAdapter


class KuaishouAdapter(PlatformAdapter):
    name = "kuaishou"
    home_url = "https://www.kuaishou.com/"
    search_inputs = (
        "input[placeholder*='搜索你感兴趣的内容']",
        "input[class*='input']",
    )
    video_cards = ("div.aspect-div", "div.cover")
    comment_buttons = (".hover-tip.commentPanel", "div[class*='comment']")
    comment_inputs = (
        "input[placeholder='说点什么...']",
        "input[placeholder*='说点什么']",
        "textarea[placeholder*='说']",
        "[contenteditable='true']",
    )
    comment_items = (
        "div[class*='comment-item']",
        "div[class*='commentItem']",
        "li[class*='comment']",
    )
    author_links = (
        "a[href*='/profile/']",
        "[class*='author'] a",
        "[class*='user-name']",
    )
    send_buttons = (
        ".send-btn",
        "button[class*='send']",
        "div[class*='send']",
        "button[type='submit']",
    )
    next_buttons = (
        ".nextVideo > .next",
        "div[class*='nextVideo']",
        "button:has-text('下一条视频')",
    )
    like_buttons = ("div[class*='like']",)

    async def search(self, keyword: str) -> bool:
        field = await self.first_visible(self.search_inputs)
        if not field:
            return False
        await field.click()
        await field.fill(keyword)
        await field.press("Enter")
        await self.page.wait_for_timeout(2_000)
        return True

    async def open_first_video(self) -> bool:
        card = await self.first_visible(self.video_cards)
        if not card:
            return False
        await card.click()
        await self.page.wait_for_timeout(2_000)
        return True

    async def next_video(self) -> bool:
        button = await self.first_visible(self.next_buttons)
        if not button:
            return False
        await button.click()
        await self.page.wait_for_timeout(1_000)
        return True

    async def open_comments(self) -> bool:
        if await self.comment_input():
            return True
        button = await self.first_visible(self.comment_buttons)
        if not button:
            return False
        await button.click()
        await self.page.wait_for_timeout(500)
        return True

    async def comment_input(self) -> Locator | None:
        return await self.first_visible(self.comment_inputs)

    async def send_button(self) -> Locator | None:
        return await self.first_visible(self.send_buttons)

    async def like_button(self) -> Locator | None:
        return await self.first_visible(self.like_buttons)
