# ComfyUI-Omnivoice

A ComfyUI custom node for [OmniVoice](https://github.com/k2-fsa/OmniVoice) — a massive multilingual zero-shot TTS model supporting 600+ languages.

## Features

- **Voice Cloning** — clone any voice from a short reference audio clip
- **Voice Design** — describe a voice with text (e.g. "female, low pitch, british accent")
- **Auto Voice** — let the model pick a voice automatically
- **Voice Presets** — built-in curated reference voices, ready to use without any audio file
- **Voice Mixing** — blend two or three reference voices for a hybrid speaker
- **EPUB Loader** — load chapters from an ebook directly into the pipeline
- **Audiobook-ready** — handles arbitrarily long text with near-constant VRAM via built-in chunking
- **Multilingual** — 600+ languages

## Installation

1. Clone into your ComfyUI custom nodes directory:
   ```bash
   cd ComfyUI/custom_nodes
   git clone https://github.com/ethanfel/ComfyUI-Omnivoice.git
   ```

2. Install via **ComfyUI Manager** (recommended) — it runs `install.py` and `requirements.txt` automatically.

   Or manually:
   ```bash
   pip install omnivoice --no-deps
   pip install -r requirements.txt
   ```
   > **Why `--no-deps` for omnivoice?** It pins `torch==2.8.*` from a CUDA 12.8 index. Installing it normally would overwrite ComfyUI's torch build. `install.py` handles this automatically; `requirements.txt` covers the remaining deps safely.

3. Restart ComfyUI. The nodes will appear under the **OmniVoice** category.

## Nodes

### OmniVoice Model Loader

Loads the OmniVoice model. Downloads automatically from HuggingFace on first run and caches to `ComfyUI/models/omnivoice/`.

| Input | Type | Description |
|-------|------|-------------|
| `device` | dropdown | `cuda:0`, `cuda:1`, or `cpu` |
| `dtype` | dropdown | `float16`, `bfloat16`, or `float32` |

**Output:** `OMNIVOICE_MODEL`

---

### OmniVoice Generate

Generates speech from text using a loaded model.

| Input | Type | Description |
|-------|------|-------------|
| `model` | OMNIVOICE_MODEL | From OmniVoice Model Loader |
| `text` | string | Text to synthesize (full pages supported) |
| `mode` | dropdown | `voice_cloning`, `voice_design`, or `auto_voice` |
| `ref_audio` | AUDIO | Reference audio for voice cloning (optional) |
| `ref_text` | string | Transcription of ref audio — connect a Whisper node for best results (optional) |
| `instruct` | string | Voice description for voice design mode (optional) |
| `speed` | float | Speed multiplier — default 1.0 |
| `num_step` | int | Diffusion steps — default 32 (use 16 for faster generation) |
| `seed` | int | Diffusion seed — set the same value across all Generate nodes in an audiobook pipeline to keep the voice consistent. 0 = random |

**Output:** `AUDIO` at 24kHz — connects directly to ComfyUI's Save Audio node.

---

### OmniVoice Voice Preset

Pre-fetched reference voices. Audio is downloaded once and cached to `ComfyUI/models/omnivoice/presets/`.

| Input | Type | Description |
|-------|------|-------------|
| `preset` | dropdown | Choose from built-in voices |

**Outputs:** `ref_audio` (AUDIO), `ref_text` (STRING) — wire directly into OmniVoice Generate.

Available presets:

| Name | Gender | Style |
|------|--------|-------|
| Shadowheart | Female | Expressive |
| American actress | Female | Theatrical |
| Podcast host | Female | Casual |
| Nature | Male | Warm |
| Old Hollywood | Male | Classic |
| Rick Sanchez | Male | Casual |
| Stewie Griffin | Male | Precise |
| Harvey Keitel | Male | Intense |
| Conan O'Brien | Male | Comedy |

---

### OmniVoice Mix Voices

Concatenates two or three reference audio clips to create a blended speaker. The model extracts a speaker embedding from the combined clip, producing a hybrid voice.

| Input | Type | Description |
|-------|------|-------------|
| `audio_1` | AUDIO | First reference voice (required) |
| `audio_2` | AUDIO | Second reference voice (required) |
| `weight_1` | float | Duration weight for audio_1 (0.0–1.0) |
| `weight_2` | float | Duration weight for audio_2 (0.0–1.0) |
| `audio_3` | AUDIO | Third reference voice (optional) |
| `weight_3` | float | Duration weight for audio_3 (optional) |
| `text_1/2/3` | string | Transcripts for each clip — merged into ref_text output |

**Outputs:** `ref_audio` (AUDIO), `ref_text` (STRING) — wire directly into OmniVoice Generate.

Weight controls how much of each clip's duration ends up in the mix. Equal weights (1.0 / 1.0) is a good starting point.

---

### OmniVoice EPUB Loader

Loads an EPUB file and outputs selected chapters as plain text, ready to pipe into OmniVoice Generate.

| Input | Type | Description |
|-------|------|-------------|
| `epub_path` | string | Absolute path to the `.epub` file |
| `chapter_start` | int | First chapter to include (1-indexed) |
| `chapter_end` | int | Last chapter to include (inclusive, auto-clamped) |

**Outputs:** `text` (STRING) — selected chapters joined by `---`, `chapter_list` (STRING) — numbered list of all chapter titles for reference.

## Default Workflow

A ready-to-use workflow is included at `workflows/voice_cloning.json`:

```
[OmniVoice Model Loader] ──────────────────────────────────┐
                                                            ▼
[OmniVoice Voice Preset] ──► ref_audio ──► [OmniVoice Generate] ──► [Save Audio]
                         └──► ref_text ──►
```

Load it via ComfyUI → Load Workflow.

## Audiobook Pipeline

For multi-chapter audiobooks, use the same seed across all Generate nodes to keep the voice consistent between paragraphs:

```
[OmniVoice Model Loader] ──────────────────────────────────────────┐
                                                                    ▼
[OmniVoice EPUB Loader] ──► chapter text ──► [OmniVoice Generate] ──► [Save Audio]
                                                      ▲
[OmniVoice Voice Preset] ──► ref_audio / ref_text ──►
                              seed = 42 (fixed)
```

## Credits

- [OmniVoice](https://github.com/k2-fsa/OmniVoice) by k2-fsa
- [OmniVoice paper](https://arxiv.org/abs/2604.00688)
