import tempfile
import os
import torch
import soundfile as sf


class OmniVoiceGenerate:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("OMNIVOICE_MODEL", {
                    "tooltip": "OmniVoice model loaded by the OmniVoice Model Loader node.",
                }),
                "text": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": (
                        "Text to synthesize. Supports inline tags for expression and pronunciation:\n"
                        "\n"
                        "NON-VERBAL SOUNDS:\n"
                        "  [laughter]           – insert a laugh\n"
                        "  [sigh]               – insert a sigh\n"
                        "\n"
                        "QUESTION / CONFIRMATION:\n"
                        "  [question-en]        – rising English question intonation\n"
                        "  [confirmation-en]    – confirmation sound\n"
                        "\n"
                        "SURPRISE:\n"
                        "  [surprise-ah]  [surprise-oh]  [surprise-wa]  [surprise-yo]\n"
                        "\n"
                        "DISSATISFACTION:\n"
                        "  [dissatisfaction-hnn]\n"
                        "\n"
                        "ENGLISH PRONUNCIATION (CMU phoneme override):\n"
                        "  You could probably still make [IH1 T] look good.\n"
                        "\n"
                        "CHINESE PRONUNCIATION (pinyin + tone number):\n"
                        "  严重SHE2本了\n"
                        "\n"
                        "EXAMPLE:\n"
                        "  [laughter] You really got me. I didn't see that coming at all."
                    ),
                }),
                "mode": (
                    ["voice_cloning", "voice_design", "auto_voice"],
                    {
                        "default": "voice_cloning",
                        "tooltip": (
                            "voice_cloning  – clone the voice from ref_audio (requires ref_audio)\n"
                            "voice_design   – describe a voice with the instruct field (requires instruct)\n"
                            "auto_voice     – model picks a voice automatically"
                        ),
                    },
                ),
            },
            "optional": {
                "ref_audio": ("AUDIO", {
                    "tooltip": "Reference audio clip to clone the voice from. Used in voice_cloning mode.",
                }),
                "ref_text": ("STRING", {
                    "default": "",
                    "tooltip": "Transcription of ref_audio. Connect a Whisper (or other STT) node for best results.",
                }),
                "language": ("STRING", {
                    "default": "auto",
                    "tooltip": (
                        "Connect the 'language' output from OmniVoice Voice Design — it sets this automatically.\n"
                        "Only needed in voice_design/auto_voice mode. Leave 'auto' for voice_cloning."
                    ),
                }),
                "instruct": ("STRING", {
                    "default": "",
                    "tooltip": (
                        "Voice style description. Required for voice_design mode; optional in voice_cloning\n"
                        "mode to attempt accent/style transfer on top of the cloned voice.\n"
                        "Connect the OmniVoice Voice Design node for structured input.\n"
                        "\n"
                        "GENDER:   male, female\n"
                        "AGE:      child, teenager, young adult, middle-aged, elderly\n"
                        "PITCH:    very low pitch, low pitch, moderate pitch, high pitch, very high pitch, whisper\n"
                        "\n"
                        "ACCENTS (only these are supported by the model):\n"
                        "  american accent, australian accent, british accent, canadian accent,\n"
                        "  chinese accent, indian accent, japanese accent, korean accent,\n"
                        "  portuguese accent, russian accent\n"
                        "\n"
                        "EXAMPLE:  female, high pitch, british accent"
                    ),
                }),
                "guidance_scale": ("FLOAT", {
                    "default": 2.0, "min": 0.0, "max": 20.0, "step": 0.1,
                    "tooltip": (
                        "Classifier-free guidance scale. Higher = more faithful to the reference/instruct, "
                        "but can over-saturate. 2.0 is a good default."
                    ),
                }),
                "speed": ("FLOAT", {
                    "default": 1.0, "min": 0.1, "max": 3.0, "step": 0.1,
                    "tooltip": "Playback speed multiplier. 1.0 = normal, >1.0 = faster, <1.0 = slower.",
                }),
                "num_step": ("INT", {
                    "default": 32, "min": 1, "max": 100,
                    "tooltip": "Diffusion steps. 32 = default quality. 16 = faster, slightly lower quality.",
                }),
                "seed": ("INT", {
                    "default": 0, "min": 0, "max": 2**32 - 1,
                    "tooltip": (
                        "Random seed for the diffusion sampler. "
                        "Set the same value across all Generate nodes in an audiobook pipeline "
                        "to keep the voice consistent between paragraphs/chapters. "
                        "0 = random (different each run)."
                    ),
                }),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "generate"
    CATEGORY = "OmniVoice"

    def generate(self, model, text, mode, ref_audio=None, ref_text="", language="auto",
                 instruct="", guidance_scale=2.0, speed=1.0, num_step=32, seed=0):
        if seed != 0:
            torch.manual_seed(seed)
        kwargs = {"text": text, "speed": speed, "num_step": num_step, "guidance_scale": guidance_scale}
        if mode != "voice_cloning" and language and language != "auto":
            kwargs["language"] = language

        if mode == "voice_cloning" and ref_audio is None:
            raise ValueError("voice_cloning mode requires ref_audio to be connected")
        if mode == "voice_design" and not instruct:
            raise ValueError("voice_design mode requires an instruct string (e.g. 'female, low pitch')")

        if mode == "voice_cloning":
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmp_path = tmp.name
            tmp.close()
            try:
                ref_waveform = ref_audio["waveform"].squeeze(0).cpu()  # (channels, samples)
                audio_np = ref_waveform.numpy()
                # soundfile expects (samples,) for mono or (samples, channels) for multi-channel
                sf.write(tmp_path, audio_np[0] if audio_np.shape[0] == 1 else audio_np.T, int(ref_audio["sample_rate"]))
                kwargs["ref_audio"] = tmp_path
                if ref_text:
                    kwargs["ref_text"] = ref_text
                if instruct:
                    kwargs["instruct"] = instruct
                audio_tensors = model.generate(**kwargs)
            finally:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

        elif mode == "voice_design" and instruct:
            kwargs["instruct"] = instruct
            audio_tensors = model.generate(**kwargs)

        else:  # auto_voice or fallback
            audio_tensors = model.generate(**kwargs)

        # Concatenate chunks: each tensor is (1, T) → concat along T → (1, T_total)
        combined = torch.cat(audio_tensors, dim=1).cpu()  # (1, T_total) on CPU
        # ComfyUI AUDIO format: (batch, channels, samples)
        waveform = combined.unsqueeze(0)  # (1, 1, T_total)

        return ({"waveform": waveform, "sample_rate": 24000},)
