import sys
import os
from pathlib import Path
from unittest.mock import MagicMock

# Ensure the project root is on sys.path so `nodes.loader` can be imported
# as a top-level package without needing to install the package.
_root = os.path.dirname(__file__)
sys.path.insert(0, _root)

# Mock omnivoice so it can be imported in tests without being installed
sys.modules.setdefault("omnivoice", MagicMock())

# Prevent pytest from treating the project root as a Python Package node.
# The root __init__.py is a ComfyUI extension entrypoint that uses relative
# imports and cannot be imported by pytest without a proper package context.
# Overriding pytest_collect_directory stops pytest from creating a Package
# node (and calling Package.setup() which imports __init__.py) for the root.
class _RootDirPlugin:
    """Registered as a plugin so it intercepts hooks before conftest scope limits."""

    def pytest_collect_directory(self, path, parent):
        # NOTE: _pytest.main.Dir is a private pytest internal (tested against pytest 8.x/9.x).
        # If collection breaks after a pytest upgrade, check if Dir moved or was renamed.
        # Alternative: add collect_ignore=["__init__.py"] at top of this file.
        from _pytest.main import Dir
        if Path(path) == Path(_root):
            # Return a plain Dir node instead of a Package node for the root,
            # so pytest skips importing __init__.py during Package.setup().
            return Dir.from_parent(parent, path=Path(path))


def pytest_configure(config):
    config.pluginmanager.register(_RootDirPlugin(), "_root_dir_plugin")
