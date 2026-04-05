class OmniVoiceVoiceDesign:
    """Compose a voice design instruct string from structured dropdowns."""

    GENDERS = ["none", "male", "female"]

    AGES = ["none", "child", "teenager", "young adult", "middle-aged", "elderly"]

    PITCHES = [
        "none",
        "very low pitch", "low pitch", "moderate pitch",
        "high pitch", "very high pitch", "whisper",
    ]

    # Exactly the accents validated by the model's _resolve_instruct() for English
    ACCENTS = [
        "none",
        "american accent", "australian accent", "british accent",
        "canadian accent", "chinese accent", "indian accent",
        "japanese accent", "korean accent", "portuguese accent",
        "russian accent",
    ]

    # Chinese dialect items validated by the model's _resolve_instruct()
    ZH_GENDERS  = ["none", "男", "女"]
    ZH_AGES     = ["none", "儿童", "少年", "青年", "中年", "老年"]
    ZH_PITCHES  = ["none", "极低音调", "低音调", "中音调", "高音调", "极高音调", "耳语"]
    ZH_DIALECTS = [
        "none",
        "东北话", "云南话", "四川话", "宁夏话", "桂林话",
        "河南话", "济南话", "甘肃话", "石家庄话", "贵州话",
        "陕西话", "青岛话",
    ]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "language": (
                    ["English", "Chinese"],
                    {
                        "default": "English",
                        "tooltip": "Selects the instruct vocabulary. The language output wires directly into Generate — no need to set it there too.",
                    },
                ),
                "gender": (cls.GENDERS, {"default": "female",
                    "tooltip": "Voice gender (English). Ignored when language is Chinese — use zh_gender."}),
                "age":    (cls.AGES,    {"default": "none",
                    "tooltip": "Age of the speaker (English). Ignored when language is Chinese — use zh_age."}),
                "pitch":  (cls.PITCHES, {"default": "none",
                    "tooltip": "Pitch (English). Ignored when language is Chinese — use zh_pitch."}),
                "accent": (cls.ACCENTS, {"default": "none",
                    "tooltip": "Accent (English only, 10 supported values)."}),
            },
            "optional": {
                "zh_gender":  (cls.ZH_GENDERS,  {"default": "none", "tooltip": "声线性别 (Chinese mode)"}),
                "zh_age":     (cls.ZH_AGES,      {"default": "none", "tooltip": "年龄段 (Chinese mode)"}),
                "zh_pitch":   (cls.ZH_PITCHES,   {"default": "none", "tooltip": "音调 (Chinese mode)"}),
                "zh_dialect": (cls.ZH_DIALECTS,  {"default": "none", "tooltip": "方言/口音 (Chinese mode)"}),
            },
        }

    RETURN_TYPES  = ("STRING", "STRING")
    RETURN_NAMES  = ("instruct", "language")
    FUNCTION      = "compose"
    CATEGORY      = "OmniVoice"

    def compose(self, language, gender, age, pitch, accent,
                zh_gender="none", zh_age="none", zh_pitch="none", zh_dialect="none"):
        if language == "Chinese":
            parts = [v for v in [zh_gender, zh_age, zh_pitch, zh_dialect] if v != "none"]
            return ("，".join(parts), "Chinese")
        else:
            parts = [v for v in [gender, age, pitch, accent] if v != "none"]
            return (", ".join(parts), "English")
