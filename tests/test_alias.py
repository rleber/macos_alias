# tests/test_alias.py

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from macos_alias.alias import MacOSAliasHandler


def test_is_available_returns_bool() -> None:
    assert isinstance(MacOSAliasHandler.is_available(), bool)


def test_non_alias_file_returns_false(tmp_path: Path) -> None:
    regular_file = tmp_path / "regular.txt"
    regular_file.write_text("data")

    symlink_file = tmp_path / "link.txt"
    symlink_file.symlink_to(regular_file)

    assert not MacOSAliasHandler.is_alias(regular_file)
    assert not MacOSAliasHandler.is_alias(symlink_file)


def test_missing_file_returns_false(tmp_path: Path) -> None:
    non_existent = tmp_path / "does_not_exist.alias"
    assert not MacOSAliasHandler.is_alias(non_existent)


@pytest.mark.skipif(
    sys.platform != "darwin" or not MacOSAliasHandler.is_available(),
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

    assert MacOSAliasHandler.update_alias(alias_file, target_file)
    assert MacOSAliasHandler.is_alias(alias_file)
    assert MacOSAliasHandler.read_target(alias_file) == target_file.resolve()

    assert MacOSAliasHandler.update_alias(alias_file, new_target_file)
    assert MacOSAliasHandler.read_target(alias_file) == new_target_file.resolve()


@pytest.mark.skipif(
    sys.platform != "darwin" or not MacOSAliasHandler.is_available(),
    reason="Requires macOS and pyobjc-framework-Cocoa",
)
def test_cocoa_exception_handling(tmp_path: Path) -> None:
    import objc

    corrupt_alias = tmp_path / "corrupt.alias"
    corrupt_alias.write_text("invalid payload")
    dummy_target = tmp_path / "target.txt"

    # Patch the internal helper method instead of the C-extension class directly
    with patch.object(MacOSAliasHandler, "is_alias", return_value=True), patch.object(
        MacOSAliasHandler,
        "_read_bookmark_data",
        side_effect=objc.error("NSInvalidArgumentException", "Bad payload", None),
    ):
        assert MacOSAliasHandler.read_target(corrupt_alias) is None
