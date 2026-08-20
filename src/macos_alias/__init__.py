__version__ = "0.2.1"

from macos_alias.alias import is_alias, make_alias, objc_is_available, target_of  # noqa
from macos_alias.cli import main

__all__ = ["MacOSAliasHandler", "main"]
