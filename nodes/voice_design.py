class OmniVoiceVoiceDesign:
    """Compose a voice design instruct string from structured dropdowns."""

    GENDERS = ["none", "male", "female"]

    AGES = ["none", "child", "teenager", "young adult", "middle-aged", "elderly"]

    PITCHES = [
        "none",
        "very low pitch", "low pitch", "moderate pitch",
        "high pitch", "very high pitch", "whisper",
    ]

    # Exactly the accents validated by the model's _resolve_instruct()
    ACCENTS = [
        "none",
        "american accent", "australian accent", "british accent",
        "canadian accent", "chinese accent", "indian accent",
        "japanese accent", "korean accent", "portuguese accent",
        "russian accent",
    ]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "gender": (cls.GENDERS, {"default": "female",
                    "tooltip": "Voice gender."}),
                "age":    (cls.AGES,    {"default": "none",
                    "tooltip": "Approximate age of the speaker."}),
                "pitch":  (cls.PITCHES, {"default": "none",
                    "tooltip": "Pitch / register of the voice."}),
                "accent": (cls.ACCENTS, {"default": "none",
                    "tooltip": "Accent validated by the model. Only these 10 are supported."}),
            },
        }

    RETURN_TYPES  = ("STRING",)
    RETURN_NAMES  = ("instruct",)
    FUNCTION      = "compose"
    CATEGORY      = "OmniVoice"

    def compose(self, gender, age, pitch, accent):
        parts = [v for v in [gender, age, pitch, accent] if v != "none"]
        return (", ".join(parts),)
