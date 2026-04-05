from .nodes import OmniVoiceModelLoader, OmniVoiceGenerate, OmniVoiceEpubLoader

NODE_CLASS_MAPPINGS = {
    "OmniVoiceModelLoader": OmniVoiceModelLoader,
    "OmniVoiceGenerate": OmniVoiceGenerate,
    "OmniVoiceEpubLoader": OmniVoiceEpubLoader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OmniVoiceModelLoader": "OmniVoice Model Loader",
    "OmniVoiceGenerate": "OmniVoice Generate",
    "OmniVoiceEpubLoader": "OmniVoice EPUB Loader",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
