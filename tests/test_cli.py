from rsi_bot.cli import build_parser


def test_cli_parser_supports_once_and_interval():
    parser = build_parser()
    args = parser.parse_args(["--config", "custom.json", "--once", "--interval", "30"])

    assert args.config == "custom.json"
    assert args.once is True
    assert args.interval == 30
