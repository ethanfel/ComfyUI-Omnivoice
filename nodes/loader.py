import os
import torch

_omnivoice_import_error = None
try:
    from omnivoice import OmniVoice
except Exception as e:
    OmniVoice = None
    _omnivoice_import_error = e

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
                "device": (
                    ["cuda:0", "cuda:1", "cpu"],
                    {"default": "cuda:0"},
                ),
                "dtype": (
                    ["float16", "bfloat16", "float32"],
                    {"default": "float16"},
                ),
                "compile": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": (
                            "Run torch.compile() on the model after loading. "
                            "First generation will be slow (~30-60s warmup) while the graph is compiled, "
                            "then every subsequent generation in the session will be faster. "
                            "Recommended for audiobook pipelines. Requires PyTorch 2.0+."
                        ),
                    },
                ),
            },
        }

    RETURN_TYPES = ("OMNIVOICE_MODEL",)
    RETURN_NAMES = ("model",)
    FUNCTION = "load_model"
    CATEGORY = "OmniVoice"

    def load_model(self, device, dtype, compile=False):
        if OmniVoice is None:
            msg = (
                "omnivoice failed to import. "
                "Install it with: pip install omnivoice --no-deps\n"
                "(On Windows embedded Python: .\\python_embeded\\python.exe -m pip install omnivoice --no-deps)\n"
            )
            if _omnivoice_import_error is not None:
                msg += f"\nOriginal error: {_omnivoice_import_error}"
            raise ImportError(msg)

        model = OmniVoice.from_pretrained(
            "k2-fsa/OmniVoice",
            device_map=device,
            dtype=DTYPE_MAP[dtype],
            cache_dir=CACHE_DIR,
        )
        if compile:
            model = torch.compile(model)
        return (model,)
