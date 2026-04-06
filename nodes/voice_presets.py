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

# Each entry: (url, transcript)
PRESETS = {
    # ── Female ──────────────────────────────────────────────────────────────
    "Shadowheart – female, expressive (Chatterbox)": (
        "https://storage.googleapis.com/chatterbox-demo-samples/prompts/female_shadowheart4.flac",
        "That place in the distance, it's huge and dedicated to Lady Shar. It can only mean one thing. I have a hidden place close to the cloister where night orchids bloom.",
    ),
    "American actress – female, theatrical (Chatterbox)": (
        "https://storage.googleapis.com/chatterbox-demo-samples/prompts/female_american.flac",
        "In this piece, we're actually playing husband and wife.",
    ),
    "Podcast host – female, casual (Chatterbox)": (
        "https://storage.googleapis.com/chatterbox-demo-samples/prompts/female_random_podcast.wav",
        "Really is, like, here is the context in which Sinead made those comments. And then also it, like, contextualizes in, like, present day Ireland. And you're like, oh, maybe Sinead was on to something. And we punished her for telling the truth. But also musicians, you know, like I was like, oh, yeah, musicians used to like any time musicians do politics, it's very dicey for them. I was like, the chicks, we were like, don't talk bad about the Iraq war. And then it turns out they were 100 percent on to something.",
    ),
    # ── Male ────────────────────────────────────────────────────────────────
    "Nature – male, warm (F5-TTS)": (
        "https://raw.githubusercontent.com/SWivid/F5-TTS/main/src/f5_tts/infer/examples/basic/basic_ref_en.wav",
        "Some call me nature, others call me mother nature.",
    ),
    "Old Hollywood – male, classic (Chatterbox)": (
        "https://storage.googleapis.com/chatterbox-demo-samples/prompts/male_old_movie.flac",
        "Yes, and you're right. Of course he will be. You'll see me in my hotel office before you leave this evening, Sid. Yes, sir. Now, Miss Gardner, let's get you the best room we have in this hotel.",
    ),
    "Rick Sanchez – male, casual (Chatterbox)": (
        "https://storage.googleapis.com/chatterbox-demo-samples/prompts/male_rickmorty.mp3",
        "You know, Grandpa goes around and he does his business in public because Grandpa isn't shady. Any of your, uh, scientists working on anything new? Why was Knight Rider called Knight Rider? I don't want to overstep my bounds or anything. It's your house. It's your world. You're a real Julius Caesar.",
    ),
    "Stewie Griffin – male, precise (Chatterbox)": (
        "https://storage.googleapis.com/chatterbox-demo-samples/prompts/male_stewie.mp3",
        "Hope I'm not bothering you. Just doing some stretching. Maybe a few poses. You'll tell me if I'm bothering you, right? I've even been singled out a few times. Probably because it's mostly pregnant women in the group. Still, Brody must see something. Although I certainly don't. But then again, I'm not the instructor, am I? Oh, yuck!",
    ),
    "Harvey Keitel – male, intense (Chatterbox)": (
        "https://storage.googleapis.com/chatterbox-demo-samples/prompts/male_harvey_keitel.mp3",
        "And if self-preservation is an instinct you possess, you better fucking do it and do it quick. So if a cop stops us and starts sticking his big snout in the car, the subterfuge won't last. But at a glance, the car will appear to be normal. We need to camouflage the interior of the car. We're gonna line the front seat and the back seat and the floorboards with quilts and blankets. So pretty please, with sugar on top. Clean the fucking car.",
    ),
    "Conan O'Brien – male, comedy (Chatterbox)": (
        "https://storage.googleapis.com/chatterbox-demo-samples/prompts/male_conan.mp3",
        "This review, the hosts quibbled over whether it's Live Free and Die Hard or Live Free or Die Hard, never even mentioning the film itself. Tangled mess. It went on for 10 minutes and then this reviewer's review was read. Good space work. And this is all really for the fake podcaster from the fake slate review while miming swiping up on his screen.",
    ),
}


_AUDIO_EXTS = {".wav", ".flac", ".mp3", ".ogg", ".m4a"}
_BUILTIN_FILES = frozenset(os.path.basename(url.split("?")[0]) for url, _ in PRESETS.values())


def _scan_user_presets():
    """Return a dict of user presets found in _CACHE_DIR.

    For each audio file that is not a cached built-in, look for a same-stem
    .txt file for the transcript.  Key format: "<stem> (local)".
    """
    user = {}
    if not os.path.isdir(_CACHE_DIR):
        return user
    for fname in sorted(os.listdir(_CACHE_DIR)):
        stem, ext = os.path.splitext(fname)
        if ext.lower() not in _AUDIO_EXTS or fname in _BUILTIN_FILES:
            continue
        audio_path = os.path.join(_CACHE_DIR, fname)
        txt_path = os.path.join(_CACHE_DIR, stem + ".txt")
        transcript = ""
        if os.path.exists(txt_path):
            with open(txt_path, "r", encoding="utf-8") as f:
                transcript = f.read().strip()
        user[f"{stem} (local)"] = (audio_path, transcript)
    return user


def _load_audio(source):
    """Load audio from a URL (downloading once) or a local file path."""
    os.makedirs(_CACHE_DIR, exist_ok=True)
    if source.startswith("http://") or source.startswith("https://"):
        filename = os.path.basename(source.split("?")[0])
        cache_path = os.path.join(_CACHE_DIR, filename)
        if not os.path.exists(cache_path):
            urllib.request.urlretrieve(source, cache_path)
        path = cache_path
    else:
        path = source
    audio_np, sr = sf.read(path, dtype="float32")
    if audio_np.ndim == 1:
        audio_np = audio_np[np.newaxis, :]        # (1, samples)
    else:
        audio_np = audio_np.T                     # (channels, samples)
    waveform = torch.from_numpy(audio_np).unsqueeze(0)  # (1, channels, samples)
    return waveform, sr


class OmniVoiceVoicePreset:
    @classmethod
    def INPUT_TYPES(cls):
        all_presets = {**PRESETS, **_scan_user_presets()}
        return {
            "required": {
                "preset": (
                    list(all_presets.keys()),
                    {
                        "tooltip": (
                            "Pre-fetched reference voice for OmniVoice Generate.\n"
                            "Connect ref_audio → ref_audio and ref_text → ref_text.\n"
                            "\n"
                            "To add your own presets, drop audio files into:\n"
                            f"  {_CACHE_DIR}\n"
                            "Add a same-name .txt file alongside for the transcript.\n"
                            "Restart ComfyUI to pick up new files."
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
        all_presets = {**PRESETS, **_scan_user_presets()}
        source, transcript = all_presets[preset]
        waveform, sr = _load_audio(source)
        return ({"waveform": waveform, "sample_rate": sr}, transcript)
