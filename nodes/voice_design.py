class OmniVoiceVoiceDesign:
    """Compose a voice design instruct string from structured dropdowns."""

    GENDERS = ["none", "male", "female"]

    AGES = ["none", "child", "teenager", "young adult", "middle-aged", "elderly"]

    PITCHES = [
        "none",
        "very low pitch", "low pitch", "moderate pitch",
        "high pitch", "very high pitch", "whisper",
    ]

    ACCENTS = [
        "none",
        # English varieties
        "american accent", "american southern accent", "american new york accent",
        "american midwest accent", "american texas accent",
        "british accent", "british rp accent", "british cockney accent",
        "scottish accent", "welsh accent", "irish accent",
        "australian accent", "new zealand accent",
        "canadian accent", "south african accent",
        # South / Southeast Asia
        "indian accent", "pakistani accent", "bangladeshi accent",
        "sri lankan accent", "singaporean accent", "malaysian accent",
        "filipino accent", "vietnamese accent", "thai accent",
        "indonesian accent",
        # East Asia
        "chinese accent", "japanese accent", "korean accent",
        # Europe
        "french accent", "german accent", "italian accent",
        "spanish accent", "portuguese accent", "dutch accent",
        "swedish accent", "norwegian accent", "danish accent",
        "finnish accent", "polish accent", "czech accent",
        "hungarian accent", "romanian accent", "greek accent",
        "turkish accent",
        # Eastern Europe / Central Asia
        "russian accent", "ukrainian accent", "arabic accent",
        "persian accent", "kazakh accent",
        # Africa / Americas
        "nigerian accent", "ghanaian accent", "kenyan accent",
        "mexican accent", "brazilian accent", "caribbean accent",
        "argentinian accent",
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
                    "tooltip": "Regional or language accent. Type to filter the list."}),
            },
        }

    RETURN_TYPES  = ("STRING",)
    RETURN_NAMES  = ("instruct",)
    FUNCTION      = "compose"
    CATEGORY      = "OmniVoice"

    def compose(self, gender, age, pitch, accent):
        parts = [v for v in [gender, age, pitch, accent] if v != "none"]
        return (", ".join(parts),)
