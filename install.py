"""
Installation script for ComfyUI-Omnivoice.

ComfyUI Manager runs this file instead of pip-installing requirements.txt directly.
We install omnivoice with --no-deps to avoid overwriting ComfyUI's torch installation.
omnivoice pins torch==2.8.* from a CUDA 12.8 custom index which would break ComfyUI.
"""
import subprocess
import sys


def pip(*args):
    subprocess.check_call([sys.executable, "-m", "pip", "install", *args])


# Install omnivoice itself without pulling in its torch/torchaudio pins.
# ComfyUI ships its own torch build — let it manage torch.
pip("omnivoice", "--no-deps")

# Install omnivoice's runtime inference dependencies (excludes torch, torchaudio,
# gradio, tensorboardX, webdataset which are training/demo-only tools).
pip(
    "transformers>=4.40.0",
    "accelerate",
    "pydub",
    "soundfile",
    "numpy",
    "beautifulsoup4",
)

print("\n[ComfyUI-Omnivoice] Installation complete.")
print("[ComfyUI-Omnivoice] NOTE: omnivoice was installed without its pinned torch.")
print("[ComfyUI-Omnivoice] If you encounter errors, ensure torch>=2.0 is installed.")
