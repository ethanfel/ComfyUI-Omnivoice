import os
import torch

try:
    from omnivoice import OmniVoice
except ImportError:
    OmniVoice = None  # type: ignore[assignment,misc]

try:
    import folder_paths
    CACHE_DIR = os.path.join(folder_paths.models_dir, "omnivoice")
except ImportError:
    CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "omnivoice")


DTYPE_MAP = {
    "float16": torch.float16,
    "bfloat16": torch.bfloat16,
    "float32": torch.float32,
}


class OmniVoiceModelLoader:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model_source": (
                    ["Auto-download (HuggingFace)", "Local path"],
                    {"default": "Auto-download (HuggingFace)"},
                ),
                "device": (
                    ["cuda:0", "cuda:1", "cpu"],
                    {"default": "cuda:0"},
                ),
                "dtype": (
                    ["float16", "bfloat16", "float32"],
                    {"default": "float16"},
                ),
            },
            "optional": {
                "local_path": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("OMNIVOICE_MODEL",)
    RETURN_NAMES = ("model",)
    FUNCTION = "load_model"
    CATEGORY = "OmniVoice"

    def load_model(self, model_source, device, dtype, local_path=""):
        if model_source == "Local path" and local_path:
            source = local_path
        else:
            source = "k2-fsa/OmniVoice"

        model = OmniVoice.from_pretrained(
            source,
            device_map=device,
            dtype=DTYPE_MAP[dtype],
            cache_dir=CACHE_DIR,
        )
        return (model,)
