import tempfile
import os
import torch
import torchaudio


class OmniVoiceGenerate:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("OMNIVOICE_MODEL",),
                "text": ("STRING", {"multiline": True, "default": ""}),
                "mode": (
                    ["voice_cloning", "voice_design", "auto_voice"],
                    {"default": "voice_cloning"},
                ),
            },
            "optional": {
                "ref_audio": ("AUDIO",),
                "ref_text": ("STRING", {"default": ""}),
                "instruct": ("STRING", {"default": ""}),
                "speed": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 3.0, "step": 0.1}),
                "num_step": ("INT", {"default": 32, "min": 1, "max": 100}),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "generate"
    CATEGORY = "OmniVoice"

    def generate(self, model, text, mode, ref_audio=None, ref_text="", instruct="", speed=1.0, num_step=32):
        kwargs = {"text": text, "speed": speed, "num_step": num_step}

        if mode == "voice_cloning" and ref_audio is None:
            raise ValueError("voice_cloning mode requires ref_audio to be connected")
        if mode == "voice_design" and not instruct:
            raise ValueError("voice_design mode requires an instruct string (e.g. 'female, low pitch')")

        if mode == "voice_cloning" and ref_audio is not None:
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmp_path = tmp.name
            tmp.close()
            try:
                waveform = ref_audio["waveform"].squeeze(0).cpu()  # (channels, samples)
                torchaudio.save(tmp_path, waveform, ref_audio["sample_rate"])
                kwargs["ref_audio"] = tmp_path
                if ref_text:
                    kwargs["ref_text"] = ref_text
                audio_tensors = model.generate(**kwargs)
            finally:
                os.unlink(tmp_path)

        elif mode == "voice_design" and instruct:
            kwargs["instruct"] = instruct
            audio_tensors = model.generate(**kwargs)

        else:  # auto_voice or fallback
            audio_tensors = model.generate(**kwargs)

        # Concatenate chunks: each tensor is (1, T) → concat along T → (1, T_total)
        combined = torch.cat(audio_tensors, dim=1)  # (1, T_total)
        # ComfyUI AUDIO format: (batch, channels, samples)
        waveform = combined.unsqueeze(0)  # (1, 1, T_total)

        return ({"waveform": waveform, "sample_rate": 24000},)
