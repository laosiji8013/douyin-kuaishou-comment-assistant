from comment_assistant.cli import build_parser


def test_live_mode_is_opt_in() -> None:
    args = build_parser().parse_args(["douyin"])
    assert args.interactive_live is False
    assert args.navigation == "manual"


def test_seed_and_limits_parse() -> None:
    args = build_parser().parse_args(
        ["kuaishou", "--seed", "42", "--max-videos", "3", "--navigation", "search"]
    )
    assert args.seed == 42
    assert args.max_videos == 3
    assert args.navigation == "search"
