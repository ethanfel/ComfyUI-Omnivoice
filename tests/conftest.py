import sys
from unittest.mock import MagicMock

# Mock omnivoice so it can be imported in tests without being installed
sys.modules.setdefault("omnivoice", MagicMock())
