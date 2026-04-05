class OmniVoiceVoiceDesign:
    """Compose a voice design instruct string from structured dropdowns."""

    GENDERS  = ["none", "male", "female"]
    AGES     = ["none", "child", "teenager", "young adult", "middle-aged", "elderly"]
    PITCHES  = ["none", "very low pitch", "low pitch", "moderate pitch", "high pitch", "very high pitch", "whisper"]
    ACCENTS  = [
        "none",
        "american accent", "british accent", "australian accent", "canadian accent",
        "indian accent", "chinese accent", "japanese accent", "korean accent",
        "portuguese accent", "russian accent",
    ]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "gender": (cls.GENDERS, {"default": "female"}),
                "age":    (cls.AGES,    {"default": "none"}),
                "pitch":  (cls.PITCHES, {"default": "none"}),
                "accent": (cls.ACCENTS, {"default": "none"}),
            },
        }

    RETURN_TYPES  = ("STRING",)
    RETURN_NAMES  = ("instruct",)
    FUNCTION      = "compose"
    CATEGORY      = "OmniVoice"

    def compose(self, gender, age, pitch, accent):
        parts = [v for v in [gender, age, pitch, accent] if v != "none"]
        return (", ".join(parts),)
