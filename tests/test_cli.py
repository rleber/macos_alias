# tests/test_cli.py

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Assumes CLI script is named cli.py; adjust import path if distinct
from macos_alias.cli import main, run_make, run_target, usage


def test_usage_exits_with_code_10(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify usage output format and exit code 10 status."""
    with pytest.raises(SystemExit) as exc_info:
        usage()

    assert exc_info.value.code == 10
    captured = capsys.readouterr()
    assert "Usage:" in captured.out


def test_main_empty_args_triggers_usage() -> None:
    """Verify empty command invocation exits with code 10."""
    with pytest.raises(SystemExit) as exc_info:
        main(["cli.py"])
    assert exc_info.value.code == 10


def test_main_invalid_subcommand_triggers_usage() -> None:
    """Verify unrecognized subcommand exits with code 10."""
    with pytest.raises(SystemExit) as exc_info:
        main(["cli.py", "invalid_cmd"])
    assert exc_info.value.code == 10


@pytest.mark.parametrize(
    "argv",
    [
        ["cli.py", "make"],  # Missing target and alias paths
        ["cli.py", "make", "/link_to"],  # Missing alias path
        ["cli.py", "make", "/link_to", "/link_at", "extra_arg"],  # Too many args
        ["cli.py", "target"],  # Missing file path
        ["cli.py", "target", "/file", "extra_arg"],  # Too many args
    ],
)
def test_main_argument_arity_mismatch(argv: list[str]) -> None:
    """Verify invalid argument counts for commands raise SystemExit(10)."""
    with pytest.raises(SystemExit) as exc_info:
        main(argv)
    assert exc_info.value.code == 10


@patch("macos_alias.MacOSAliasHandler.update_alias")
def test_run_make_success(
    mock_update: MagicMock, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verify stdout output when alias creation succeeds."""
    mock_update.return_value = True

    run_make("/path/to/target", "/path/to/alias")

    # Order of parameters in CLI script pass (link_at, link_to) to update_alias
    mock_update.assert_called_once_with(Path("/path/to/alias"), Path("/path/to/target"))
    captured = capsys.readouterr()
    assert captured.out.strip() == "Alias made"


@patch("macos_alias.MacOSAliasHandler.update_alias")
def test_run_make_failure(
    mock_update: MagicMock, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verify stdout output when alias creation fails."""
    mock_update.return_value = False

    run_make("/path/to/target", "/path/to/alias")

    mock_update.assert_called_once_with(Path("/path/to/alias"), Path("/path/to/target"))
    captured = capsys.readouterr()
    assert captured.out.strip() == "Failed to make alias"


@patch("macos_alias.MacOSAliasHandler.read_target")
def test_run_target(mock_read: MagicMock, capsys: pytest.CaptureFixture[str]) -> None:
    """Verify stdout output when resolving alias target path."""
    mock_read.return_value = Path("/resolved/target/path")

    run_target("/path/to/alias")

    mock_read.assert_called_once_with(Path("/path/to/alias"))
    captured = capsys.readouterr()
    assert captured.out.strip() == "/resolved/target/path"


@patch("macos_alias.cli.run_make")
def test_main_dispatch_make(mock_run_make: MagicMock) -> None:
    """Verify main routes 'make' subcommand correctly and supports case-insensitivity."""
    main(["macos_alias.py", "MAKE", "/target/path", "/alias/path"])
    mock_run_make.assert_called_once_with("/target/path", "/alias/path")


@patch("macos_alias.cli.run_target")
def test_main_dispatch_target(mock_run_target: MagicMock) -> None:
    """Verify main routes 'target' subcommand correctly."""
    main(["cli.py", "target", "/alias/path"])
    mock_run_target.assert_called_once_with("/alias/path")
