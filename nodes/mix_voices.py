import torch


def _to_mono(waveform):
    """(1, channels, samples) → (1, 1, samples)"""
    if waveform.shape[1] > 1:
        return waveform.mean(dim=1, keepdim=True)
    return waveform


def _resample(waveform, src_sr, dst_sr):
    """Resample waveform tensor (1, 1, samples) to dst_sr."""
    if src_sr == dst_sr:
        return waveform
    try:
        import torchaudio
        resampler = torchaudio.transforms.Resample(orig_freq=src_sr, new_freq=dst_sr)
        return resampler(waveform)
    except Exception:
        # fallback: nearest-neighbour via interpolate
        ratio = dst_sr / src_sr
        new_len = int(waveform.shape[-1] * ratio)
        return torch.nn.functional.interpolate(
            waveform.float(), size=new_len, mode='linear', align_corners=False
        )


class OmniVoiceMixVoices:
    """Concatenate two (or three) reference voices to create a blended speaker embedding."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio_1": ("AUDIO", {
                    "tooltip": "First reference voice.",
                }),
                "audio_2": ("AUDIO", {
                    "tooltip": "Second reference voice.",
                }),
                "weight_1": ("FLOAT", {
                    "default": 1.0, "min": 0.0, "max": 1.0, "step": 0.05,
                    "tooltip": "Relative duration weight for audio_1. Higher = more of this voice in the mix.",
                }),
                "weight_2": ("FLOAT", {
                    "default": 1.0, "min": 0.0, "max": 1.0, "step": 0.05,
                    "tooltip": "Relative duration weight for audio_2.",
                }),
            },
            "optional": {
                "audio_3": ("AUDIO", {
                    "tooltip": "Optional third reference voice.",
                }),
                "weight_3": ("FLOAT", {
                    "default": 1.0, "min": 0.0, "max": 1.0, "step": 0.05,
                    "tooltip": "Relative duration weight for audio_3.",
                }),
                "text_1": ("STRING", {
                    "default": "",
                    "tooltip": "Transcript for audio_1.",
                }),
                "text_2": ("STRING", {
                    "default": "",
                    "tooltip": "Transcript for audio_2.",
                }),
                "text_3": ("STRING", {
                    "default": "",
                    "tooltip": "Transcript for audio_3 (optional).",
                }),
            },
        }

    RETURN_TYPES = ("AUDIO", "STRING")
    RETURN_NAMES = ("ref_audio", "ref_text")
    FUNCTION = "mix"
    CATEGORY = "OmniVoice"

    def mix(self, audio_1, audio_2, weight_1=1.0, weight_2=1.0,
            audio_3=None, weight_3=1.0,
            text_1="", text_2="", text_3=""):

        audios = [audio_1, audio_2]
        weights = [weight_1, weight_2]
        texts = [text_1, text_2]
        if audio_3 is not None:
            audios.append(audio_3)
            weights.append(weight_3)
            texts.append(text_3)

        # Use the highest sample rate among inputs as target
        target_sr = max(a["sample_rate"] for a in audios)

        clips = []
        for audio, weight in zip(audios, weights):
            w = _to_mono(audio["waveform"])           # (1, 1, samples)
            w = _resample(w, audio["sample_rate"], target_sr)

            # trim/repeat to match requested weight in seconds (normalise later)
            clips.append((w, weight))

        # Determine target samples per unit weight
        # Scale each clip so that weight=1.0 keeps its full length,
        # and trim/tile accordingly relative to the largest weighted clip.
        max_samples = max(c.shape[-1] * wt for c, wt in clips)
        target_per_unit = max_samples  # samples for weight=1.0

        trimmed = []
        for clip, weight in clips:
            n_samples = int(target_per_unit * weight)
            if n_samples <= 0:
                continue
            src_len = clip.shape[-1]
            if src_len >= n_samples:
                trimmed.append(clip[..., :n_samples])
            else:
                # tile then trim
                reps = (n_samples // src_len) + 1
                tiled = clip.repeat(1, 1, reps)
                trimmed.append(tiled[..., :n_samples])

        mixed = torch.cat(trimmed, dim=-1)  # (1, 1, total_samples)

        merged_text = " ".join(t.strip() for t in texts if t.strip())

        return ({"waveform": mixed, "sample_rate": target_sr}, merged_text)
