# tests/test_cli.py

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from macos_alias import __version__
from macos_alias.cli import build_parser, main


def test_parser_version_flag_long(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify --version flag outputs prog name and version string, exiting with code 0."""
    parser = build_parser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--version"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert f"macos_alias {__version__}" in captured.out


def test_parser_version_flag_short(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify -v flag outputs prog name and version string, exiting with code 0."""
    parser = build_parser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["-v"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert f"macos_alias {__version__}" in captured.out


def test_parser_make_subcommand() -> None:
    """Verify CLI parser correctly maps arguments for 'make' command."""
    parser = build_parser()
    args = parser.parse_args(["make", "/path/to/target", "/path/to/alias"])

    assert args.command == "make"
    assert args.link_to == "/path/to/target"
    assert args.link_at == "/path/to/alias"


def test_parser_target_subcommand() -> None:
    """Verify CLI parser correctly maps arguments for 'target' command."""
    parser = build_parser()
    args = parser.parse_args(["target", "/path/to/alias"])

    assert args.command == "target"
    assert args.file == "/path/to/alias"


def test_parser_missing_subcommand() -> None:
    """Verify parser exits with code 2 when no subcommand or version flag is provided."""
    parser = build_parser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args([])

    assert exc_info.value.code == 2


@pytest.mark.parametrize(
    "argv",
    [
        ["make"],
        ["make", "/only_one_arg"],
        ["target"],
    ],
)
def test_parser_invalid_arity(argv: list[str]) -> None:
    """Verify parser exits with code 2 on parameter count mismatch."""
    parser = build_parser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(argv)

    assert exc_info.value.code == 2


@patch("macos_alias.cli.make_alias")
def test_main_make_success(
    mock_update: MagicMock, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verify successful stdout and return code when 'make' succeeds."""
    mock_update.return_value = True

    exit_code = main(["make", "/target/file.txt", "/alias/file.alias"])

    assert exit_code == 0
    mock_update.assert_called_once_with(
        Path("/alias/file.alias"), Path("/target/file.txt")
    )
    captured = capsys.readouterr()
    assert captured.out.strip() == ""  # Function is terse


@patch("macos_alias.cli.make_alias")
def test_main_make_failure(
    mock_update: MagicMock, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verify stdout and return code when 'make' fails."""
    mock_update.return_value = False

    exit_code = main(["make", "/target/file.txt", "/alias/file.alias"])

    assert exit_code == 1
    mock_update.assert_called_once_with(
        Path("/alias/file.alias"), Path("/target/file.txt")
    )
    captured = capsys.readouterr()
    assert captured.out.strip() == ""  # Function is terse


@patch("macos_alias.cli.target_of")
def test_main_target_resolution(
    mock_read: MagicMock, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verify target path output and return code for 'target' subcommand."""
    mock_read.return_value = Path("/resolved/target/file.txt")

    exit_code = main(["target", "/alias/file.alias"])

    assert exit_code == 0
    mock_read.assert_called_once_with(Path("/alias/file.alias"))
    captured = capsys.readouterr()
    assert captured.out.strip() == "/resolved/target/file.txt"
