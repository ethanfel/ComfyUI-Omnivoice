import sys
import os

# Ensure the project root is on sys.path so `nodes.loader` can be imported
# as a top-level package without needing to install the package.
sys.path.insert(0, os.path.dirname(__file__))
