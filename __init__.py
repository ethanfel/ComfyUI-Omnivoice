from .nodes import OmniVoiceModelLoader, OmniVoiceGenerate

NODE_CLASS_MAPPINGS = {
    "OmniVoiceModelLoader": OmniVoiceModelLoader,
    "OmniVoiceGenerate": OmniVoiceGenerate,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OmniVoiceModelLoader": "OmniVoice Model Loader",
    "OmniVoiceGenerate": "OmniVoice Generate",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
