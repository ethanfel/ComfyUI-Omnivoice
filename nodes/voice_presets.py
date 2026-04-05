import os
import urllib.request
import numpy as np
import torch
import soundfile as sf

try:
    import folder_paths
    _CACHE_DIR = os.path.join(folder_paths.models_dir, "omnivoice", "presets")
except ImportError:
    _CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "omnivoice", "presets")

# Each entry: (display_name, url, transcript)
# transcript="" means unknown — connect a Whisper node to ref_text to fill it.
PRESETS = {
    "Nature – female, warm (F5-TTS ref)": (
        "https://raw.githubusercontent.com/SWivid/F5-TTS/main/src/f5_tts/infer/examples/basic/basic_ref_en.wav",
        "Some call me nature, others call me mother nature.",
    ),
    "Shadowheart – female, expressive (Chatterbox ref)": (
        "https://storage.googleapis.com/chatterbox-demo-samples/prompts/female_shadowheart4.flac",
        "",  # transcript unknown — connect Whisper node to ref_text
    ),
}


def _load_audio(url):
    """Download (once) and return (waveform_tensor, sample_rate)."""
    os.makedirs(_CACHE_DIR, exist_ok=True)
    filename = os.path.basename(url.split("?")[0])
    cache_path = os.path.join(_CACHE_DIR, filename)
    if not os.path.exists(cache_path):
        urllib.request.urlretrieve(url, cache_path)
    audio_np, sr = sf.read(cache_path, dtype="float32")
    if audio_np.ndim == 1:
        audio_np = audio_np[np.newaxis, :]        # (1, samples)
    else:
        audio_np = audio_np.T                     # (channels, samples)
    waveform = torch.from_numpy(audio_np).unsqueeze(0)  # (1, channels, samples)
    return waveform, sr


class OmniVoiceVoicePreset:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "preset": (
                    list(PRESETS.keys()),
                    {
                        "tooltip": (
                            "Pre-fetched reference voice for OmniVoice Generate.\n"
                            "Connect ref_audio → ref_audio and ref_text → ref_text.\n"
                            "If ref_text is blank, connect a Whisper node to supply the transcript."
                        ),
                    },
                ),
            },
        }

    RETURN_TYPES = ("AUDIO", "STRING")
    RETURN_NAMES = ("ref_audio", "ref_text")
    FUNCTION = "load_preset"
    CATEGORY = "OmniVoice"

    def load_preset(self, preset):
        url, transcript = PRESETS[preset]
        waveform, sr = _load_audio(url)
        return ({"waveform": waveform, "sample_rate": sr}, transcript)
