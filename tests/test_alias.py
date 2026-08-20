# tests/test_alias.py

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from macos_alias.alias import is_alias, make_alias, objc_is_available, target_of


def test_is_available_returns_bool() -> None:
    assert isinstance(objc_is_available(), bool)


def test_non_alias_file_returns_false_and_none(tmp_path: Path) -> None:
    regular_file = tmp_path / "regular.txt"
    regular_file.write_text("data")

    symlink_file = tmp_path / "link.txt"
    symlink_file.symlink_to(regular_file)

    assert not is_alias(regular_file)
    assert not is_alias(symlink_file)
    # Validate read_target return values on non-alias files
    assert target_of(regular_file) is None
    assert target_of(symlink_file) is None


def test_missing_file_returns_false_and_none(tmp_path: Path) -> None:
    non_existent = tmp_path / "does_not_exist.alias"
    assert not is_alias(non_existent)
    assert target_of(non_existent) is None


@pytest.mark.skipif(
    sys.platform != "darwin" or not objc_is_available(),
    reason="Requires macOS and pyobjc-framework-Cocoa",
)
def test_alias_lifecycle(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    dest_dir = tmp_path / "dest"
    source_dir.mkdir()
    dest_dir.mkdir()

    target_file = source_dir / "file.txt"
    target_file.write_text("content_a")

    new_target_file = dest_dir / "file.txt"
    new_target_file.write_text("content_b")

    alias_file = source_dir / "file.alias"

    assert make_alias(alias_file, target_file)
    assert is_alias(alias_file)
    assert target_of(alias_file) == target_file.resolve()

    assert make_alias(alias_file, new_target_file)
    assert target_of(alias_file) == new_target_file.resolve()


@pytest.mark.skipif(
    sys.platform != "darwin" or not objc_is_available(),
    reason="Requires macOS and pyobjc-framework-Cocoa",
)
def test_cocoa_exception_handling(tmp_path: Path) -> None:
    import objc

    corrupt_alias = tmp_path / "corrupt.alias"
    corrupt_alias.write_text("invalid payload")

    with (
        patch("macos_alias.alias.is_alias", return_value=True),
        patch(
            "macos_alias.alias._read_bookmark_data",
            side_effect=objc.error("NSInvalidArgumentException", "Bad payload", None),
        ),
    ):
        assert target_of(corrupt_alias) is None
