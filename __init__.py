try:
    from .nodes import OmniVoiceModelLoader, OmniVoiceGenerate

    NODE_CLASS_MAPPINGS = {
        "OmniVoiceModelLoader": OmniVoiceModelLoader,
        "OmniVoiceGenerate": OmniVoiceGenerate,
    }

    NODE_DISPLAY_NAME_MAPPINGS = {
        "OmniVoiceModelLoader": "OmniVoice Model Loader",
        "OmniVoiceGenerate": "OmniVoice Generate",
    }
except ImportError:
    # Graceful fallback when loaded outside of a package context (e.g. pytest)
    NODE_CLASS_MAPPINGS = {}
    NODE_DISPLAY_NAME_MAPPINGS = {}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
