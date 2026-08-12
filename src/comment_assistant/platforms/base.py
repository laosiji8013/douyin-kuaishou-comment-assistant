from __future__ import annotations

from abc import ABC, abstractmethod

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Locator, Page


class PlatformAdapter(ABC):
    name: str
    home_url: str
    comment_items: tuple[str, ...] = ()
    author_links: tuple[str, ...] = ()

    def __init__(self, page: Page):
        self.page = page

    async def open_home(self) -> None:
        await self.page.goto(self.home_url, wait_until="domcontentloaded", timeout=30_000)

    async def first_visible(self, selectors: tuple[str, ...]) -> Locator | None:
        for selector in selectors:
            candidates = self.page.locator(selector)
            for index in range(await candidates.count()):
                candidate = candidates.nth(index)
                try:
                    if await candidate.is_visible():
                        return candidate
                except PlaywrightError:
                    continue
        return None

    async def hover_visible_comment(self) -> bool:
        item = await self.first_visible(self.comment_items)
        if not item:
            return False
        await item.hover()
        return True

    async def hover_author(self) -> bool:
        author = await self.first_visible(self.author_links)
        if not author:
            return False
        await author.hover()
        return True

    @abstractmethod
    async def search(self, keyword: str) -> bool: ...

    @abstractmethod
    async def open_first_video(self) -> bool: ...

    @abstractmethod
    async def next_video(self) -> bool: ...

    @abstractmethod
    async def open_comments(self) -> bool: ...

    @abstractmethod
    async def comment_input(self) -> Locator | None: ...

    @abstractmethod
    async def send_button(self) -> Locator | None: ...

    @abstractmethod
    async def like_button(self) -> Locator | None: ...
