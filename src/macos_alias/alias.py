# src/macos_alias/alias.py

import logging
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

logger = logging.getLogger(__name__)


class MacOSAliasHandler:
    """Encapsulates macOS Finder Alias (BookmarkData) detection and updates."""

    @staticmethod
    def is_available() -> bool:
        """Checks if PyObjC Cocoa bindings are installed."""
        return HAS_PYOBJC

    @classmethod
    def _read_bookmark_data(cls, alias_url: NSURL) -> tuple:
        """Internal Cocoa wrapper to avoid patching PyObjC C-extensions directly in unit tests."""
        return NSURL.bookmarkDataWithContentsOfURL_error_(alias_url, None)

    @classmethod
    def is_alias(cls, file_path: Path) -> bool:
        """Determines if a path corresponds to a macOS Finder Alias file."""
        if not cls.is_available() or file_path.is_symlink() or not file_path.is_file():
            return False

        try:
            file_url = NSURL.fileURLWithPath_(str(file_path))
            # Must use Foundation.NSURLIsAliasFileKey constant instead of raw string
            resource_values, error = file_url.resourceValuesForKeys_error_(
                [NSURLIsAliasFileKey], None
            )
            if error or not resource_values:
                return False
            return bool(resource_values.get(NSURLIsAliasFileKey, False))
        except (OSError, objc.error) as err:
            logger.warning("Failed determining alias state for %s: %s", file_path, err)
            return False

    @classmethod
    def update_alias(cls, alias_path: Path, new_target: Path) -> bool:
        """Updates or creates a macOS Finder Alias (BookmarkData) referencing new_target."""
        if not cls.is_available():
            logger.warning(
                "pyobjc-framework-Cocoa not installed; skipping update for %s",
                alias_path,
            )
            return False

        try:
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
                logger.error(
                    "Failed creating bookmark data for %s: %s", new_target, error
                )
                return False

            success, error = NSURL.writeBookmarkData_toURL_options_error_(
                bookmark_data,
                alias_url,
                NSURLBookmarkCreationSuitableForBookmarkFile,
                None,
            )
            if not success or error:
                logger.error(
                    "Failed writing updated alias to %s: %s", alias_path, error
                )
                return False
            return True
        except (OSError, PermissionError) as err:
            logger.error("I/O failure updating macOS alias at %s: %s", alias_path, err)
            return False
        except objc.error as err:
            logger.error(
                "Cocoa API runtime error updating alias %s: %s", alias_path, err
            )
            return False

    @classmethod
    def read_target(cls, alias_path: Path) -> Path | None:
        if not cls.is_alias(alias_path):
            return False
        try:
            alias_url = NSURL.fileURLWithPath_(str(alias_path))
            bookmark_data, bm_err = cls._read_bookmark_data(alias_url)
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
        except (OSError, PermissionError) as err:
            logger.warning(
                "I/O error inspecting macOS alias at %s: %s", alias_path, err
            )
        except (objc.error, ValueError) as err:
            logger.warning("Malformed bookmark data at %s: %s", alias_path, err)
        return None
