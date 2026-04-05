from .nodes import OmniVoiceModelLoader, OmniVoiceGenerate, OmniVoiceEpubLoader, OmniVoiceVoicePreset, OmniVoiceMixVoices, OmniVoiceVoiceDesign

NODE_CLASS_MAPPINGS = {
    "OmniVoiceModelLoader": OmniVoiceModelLoader,
    "OmniVoiceGenerate": OmniVoiceGenerate,
    "OmniVoiceEpubLoader": OmniVoiceEpubLoader,
    "OmniVoiceVoicePreset": OmniVoiceVoicePreset,
    "OmniVoiceMixVoices": OmniVoiceMixVoices,
    "OmniVoiceVoiceDesign": OmniVoiceVoiceDesign,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OmniVoiceModelLoader": "OmniVoice Model Loader",
    "OmniVoiceGenerate": "OmniVoice Generate",
    "OmniVoiceEpubLoader": "OmniVoice EPUB Loader",
    "OmniVoiceVoicePreset": "OmniVoice Voice Preset",
    "OmniVoiceMixVoices": "OmniVoice Mix Voices",
    "OmniVoiceVoiceDesign": "OmniVoice Voice Design",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
