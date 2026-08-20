# src/macos_alias/alias.py

from contextlib import suppress
from pathlib import Path

try:
    import objc
    from Foundation import (
        NSURL,
        NSURLBookmarkCreationSuitableForBookmarkFile,
        NSURLBookmarkResolutionWithoutUI,
        NSURLIsAliasFileKey,
    )

    HAS_PYOBJC = True
except ImportError:
    HAS_PYOBJC = False
    objc = None


def objc_is_available() -> bool:
    """Checks if PyObjC Cocoa bindings are installed."""
    return HAS_PYOBJC


def _read_bookmark_data(alias_url: NSURL) -> tuple:
    """Internal Cocoa wrapper to avoid patching PyObjC C-extensions directly in unit tests."""
    return NSURL.bookmarkDataWithContentsOfURL_error_(alias_url, None)


def is_alias(file_path: Path) -> bool:
    """Determines if a path corresponds to a macOS Finder Alias file."""
    if not objc_is_available() or file_path.is_symlink() or not file_path.is_file():
        return False

    with suppress(OSError, objc.error):
        file_url = NSURL.fileURLWithPath_(str(file_path))
        resource_values, error = file_url.resourceValuesForKeys_error_(
            [NSURLIsAliasFileKey], None
        )
        if error or not resource_values:
            return False
        return bool(resource_values.get(NSURLIsAliasFileKey, False))

    return False


def make_alias(alias_path: Path, new_target: Path) -> bool:
    """Updates or creates a macOS Finder Alias (BookmarkData) referencing new_target."""
    if not objc_is_available():
        return False

    with suppress(OSError, PermissionError, objc.error):
        alias_url = NSURL.fileURLWithPath_(str(alias_path))
        new_target_url = NSURL.fileURLWithPath_(str(new_target))

        bookmark_data, error = (
            new_target_url.bookmarkDataWithOptions_includingResourceValuesForKeys_relativeToURL_error_(
                NSURLBookmarkCreationSuitableForBookmarkFile,
                None,
                None,
                None,
            )
        )
        if error or not bookmark_data:
            return False

        success, error = NSURL.writeBookmarkData_toURL_options_error_(
            bookmark_data,
            alias_url,
            NSURLBookmarkCreationSuitableForBookmarkFile,
            None,
        )
        return success and not error

    return False


def target_of(alias_path: Path) -> Path | None:
    """Resolves a macOS Finder Alias path to its target Path, returning None if invalid."""
    if not is_alias(alias_path):
        return None

    with suppress(OSError, PermissionError, objc.error, ValueError):
        alias_url = NSURL.fileURLWithPath_(str(alias_path))
        bookmark_data, bm_err = _read_bookmark_data(alias_url)
        if bm_err or not bookmark_data:
            return None

        (
            resolved_url,
            _,
            res_err,
        ) = NSURL.URLByResolvingBookmarkData_options_relativeToURL_bookmarkDataIsStale_error_(
            bookmark_data,
            NSURLBookmarkResolutionWithoutUI,
            None,
            None,
            None,
        )
        if not res_err and resolved_url:
            return Path(resolved_url.path()).resolve()

    return None
