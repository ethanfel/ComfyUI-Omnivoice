from .nodes import OmniVoiceModelLoader, OmniVoiceGenerate, OmniVoiceEpubLoader, OmniVoiceVoicePreset

NODE_CLASS_MAPPINGS = {
    "OmniVoiceModelLoader": OmniVoiceModelLoader,
    "OmniVoiceGenerate": OmniVoiceGenerate,
    "OmniVoiceEpubLoader": OmniVoiceEpubLoader,
    "OmniVoiceVoicePreset": OmniVoiceVoicePreset,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OmniVoiceModelLoader": "OmniVoice Model Loader",
    "OmniVoiceGenerate": "OmniVoice Generate",
    "OmniVoiceEpubLoader": "OmniVoice EPUB Loader",
    "OmniVoiceVoicePreset": "OmniVoice Voice Preset",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
