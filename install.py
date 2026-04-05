"""
ComfyUI Manager calls this file before installing requirements.txt.

omnivoice cannot be listed in requirements.txt because its default install
pins torch==2.8.* from a CUDA 12.8 index, which would overwrite ComfyUI's
torch build. We install it here with --no-deps to skip that pin.
All other dependencies are declared normally in requirements.txt.
"""
import subprocess
import sys


def _installed(package):
    import importlib.util
    return importlib.util.find_spec(package) is not None


if not _installed("omnivoice"):
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "omnivoice", "--no-deps"
    ])
