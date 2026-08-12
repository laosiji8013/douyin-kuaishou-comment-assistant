from __future__ import annotations

import argparse
import asyncio
from importlib.resources import files
from pathlib import Path

from playwright.async_api import async_playwright

from .config import AppConfig, load_string_list
from .platforms import DouyinAdapter, KuaishouAdapter
from .session import open_browser, run_session

ROOT = Path(__file__).resolve().parents[2]
RESOURCE_ROOT = files("comment_assistant").joinpath("resources")


def _default_path(repository_path: Path, resource_name: str) -> Path:
    if repository_path.exists():
        return repository_path
    return Path(str(RESOURCE_ROOT.joinpath(resource_name)))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="抖音/快手交互式评论助手：支持随机节奏，但每次互动必须人工确认。"
    )
    parser.add_argument("platform", choices=("douyin", "kuaishou"))
    parser.add_argument(
        "--config",
        type=Path,
        default=_default_path(ROOT / "config/default.json", "default.json"),
    )
    parser.add_argument(
        "--comments",
        type=Path,
        default=_default_path(ROOT / "data/comments.example.json", "comments.example.json"),
    )
    parser.add_argument(
        "--keywords",
        type=Path,
        default=_default_path(ROOT / "data/keywords.example.json", "keywords.example.json"),
    )
    parser.add_argument("--keyword", help="覆盖关键词文件并使用这个词")
    parser.add_argument("--navigation", choices=("manual", "search"), default="manual")
    parser.add_argument("--max-videos", type=int)
    parser.add_argument("--seed", type=int, help="固定随机种子，方便复现与测试")
    parser.add_argument(
        "--interactive-live",
        action="store_true",
        help="允许在每条两次人工确认后发送；默认 dry-run 不触发平台互动",
    )
    return parser


async def async_main(args: argparse.Namespace) -> int:
    config = AppConfig.load(args.config)
    comments = load_string_list(args.comments, "comments")
    keywords = load_string_list(args.keywords, "keywords")
    keyword = args.keyword or keywords[0]
    max_videos = args.max_videos or int(config.session["default_max_videos"])
    if max_videos < 1:
        raise ValueError("max-videos must be >= 1")
    dry_run = not args.interactive_live

    print("=" * 68)
    print(f"平台：{args.platform} | 导航：{args.navigation} | 最多：{max_videos} 条")
    print(f"模式：{'逐条人工确认的实时模式' if not dry_run else 'dry-run（不发送、不点赞）'}")
    print("随机计划只决定等待和候选事件，不会绕过人工确认。")
    print("=" * 68)
    if not dry_run:
        confirmation = input("实时模式会操作真实账号。输入 INTERACTIVE LIVE 继续：").strip()
        if confirmation != "INTERACTIVE LIVE":
            print("未通过启动确认，已退出。")
            return 2

    factory = DouyinAdapter if args.platform == "douyin" else KuaishouAdapter
    async with async_playwright() as playwright:
        context = await open_browser(playwright, config.browser)
        try:
            await run_session(
                factory,
                context,
                config,
                comments,
                keyword,
                args.navigation,
                max_videos,
                dry_run,
                args.seed,
            )
        finally:
            await context.close()
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return asyncio.run(async_main(args))
    except KeyboardInterrupt:
        print("\n用户终止，会话已结束。")
        return 130
    except (OSError, ValueError, RuntimeError) as error:
        print(f"错误：{error}")
        return 1
