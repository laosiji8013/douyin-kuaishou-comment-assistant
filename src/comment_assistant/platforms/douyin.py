from __future__ import annotations

from playwright.async_api import Locator

from .base import PlatformAdapter


class DouyinAdapter(PlatformAdapter):
    name = "douyin"
    home_url = "https://www.douyin.com/"
    search_inputs = (
        "input[type='text']",
        "input[placeholder*='搜索']",
        "input[placeholder*='找视频']",
    )
    video_cards = (
        "div[class*='video-card']",
        "a[class*='video']",
        "img[class*='cover']",
    )
    comment_buttons = (
        "a[class*='comment']",
        "span[class*='comment']",
        "[class*='comment-icon']",
    )
    comment_inputs = (
        "input[placeholder*='留下']",
        "input[placeholder*='说点']",
        "textarea[placeholder*='评论']",
        "div[contenteditable='true'][class*='comment']",
        "[contenteditable='true']",
    )
    comment_items = (
        "div[class*='comment-item']",
        "div[data-e2e*='comment']",
        "li[class*='comment']",
    )
    author_links = (
        "a[href*='/user/']",
        "[class*='author'] a",
        "[class*='nickname']",
    )
    send_buttons = (
        "button[class*='send']",
        "button:has-text('发送')",
        "button[type='submit']",
        "[class*='SendBtn']",
    )
    next_buttons = (
        "div[class*='next-video']",
        "div[class*='nextVideo']",
        "button:has-text('下一条')",
    )
    like_buttons = ("[class*='like-icon']", "[class*='like'] button")

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
        if button:
            await button.click()
        else:
            await self.page.keyboard.press("ArrowDown")
        await self.page.wait_for_timeout(1_000)
        return True

    async def open_comments(self) -> bool:
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
