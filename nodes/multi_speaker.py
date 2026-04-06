class OmniVoiceSpeaker:
    """Bundle a label, reference audio, and optional transcript into a speaker slot."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "label": ("STRING", {
                    "default": "Narrator",
                    "tooltip": (
                        "Name used to identify this speaker.\n"
                        "In tagged_speakers mode, prefix paragraphs with [Label]:\n"
                        "  [Narrator] Once upon a time...\n"
                        "In alternate_paragraphs mode the label is informational only."
                    ),
                }),
                "ref_audio": ("AUDIO", {
                    "tooltip": "Reference audio clip for this speaker's voice.",
                }),
            },
            "optional": {
                "ref_text": ("STRING", {
                    "default": "",
                    "tooltip": "Transcript of ref_audio. Improves cloning quality.",
                }),
            },
        }

    RETURN_TYPES = ("OMNIVOICE_SPEAKER",)
    RETURN_NAMES = ("speaker",)
    FUNCTION = "build"
    CATEGORY = "OmniVoice"

    def build(self, label, ref_audio, ref_text=""):
        return ({"label": label, "ref_audio": ref_audio, "ref_text": ref_text},)


class OmniVoiceSpeakers:
    """Collect multiple speakers into a roster for multi-speaker generation.

    The number of speaker input slots expands dynamically when num_speakers changes
    (requires the OmniVoice web extension to be loaded by ComfyUI).
    Connect one OmniVoice Speaker node per slot.
    """

    @classmethod
    def INPUT_TYPES(cls):
        # speaker_1…speaker_8 are declared here so ComfyUI validation accepts them.
        # Visibility is controlled by the JS extension (web/multi_speaker.js):
        # only the first num_speakers slots are shown as live inputs.
        optional_speakers = {
            f"speaker_{i}": ("OMNIVOICE_SPEAKER", {})
            for i in range(1, 9)
        }
        return {
            "required": {
                "num_speakers": ("INT", {
                    "default": 2, "min": 2, "max": 8, "step": 1,
                    "tooltip": (
                        "Number of active speaker slots.\n"
                        "Changing this value adds or removes speaker_N inputs on the node."
                    ),
                }),
                "mode": (
                    ["alternate_paragraphs", "tagged_speakers"],
                    {
                        "default": "alternate_paragraphs",
                        "tooltip": (
                            "alternate_paragraphs – paragraphs (separated by blank lines) rotate\n"
                            "  through speakers in order: 1 → 2 → 3 → 1 → …\n"
                            "\n"
                            "tagged_speakers – prefix each paragraph with [Label] to assign\n"
                            "  a specific speaker. Labels must match those on the Speaker nodes.\n"
                            "  Unrecognised tags fall back to speaker 1.\n"
                            "\n"
                            "  Example:\n"
                            "  [Narrator] The door creaked open.\n"
                            "\n"
                            "  [Alice] Who is there?"
                        ),
                    },
                ),
            },
            "optional": optional_speakers,
        }

    RETURN_TYPES = ("OMNIVOICE_SPEAKERS",)
    RETURN_NAMES = ("speakers",)
    FUNCTION = "build"
    CATEGORY = "OmniVoice"

    def build(self, num_speakers, mode, **kwargs):
        speakers = []
        for i in range(1, num_speakers + 1):
            spk = kwargs.get(f"speaker_{i}")
            if spk is not None:
                speakers.append(spk)
        if len(speakers) < 2:
            raise ValueError(
                f"OmniVoice Speakers: at least 2 speakers must be connected "
                f"(got {len(speakers)})."
            )
        return ({"speakers": speakers, "mode": mode},)
