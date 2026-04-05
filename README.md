# ComfyUI-Omnivoice

A ComfyUI custom node for [OmniVoice](https://github.com/k2-fsa/OmniVoice) — a massive multilingual zero-shot TTS model supporting 600+ languages.

## Features

- **Voice Cloning** — clone any voice from a short reference audio clip
- **Voice Design** — describe a voice with text (e.g. "female, low pitch, british accent")
- **Auto Voice** — let the model pick a voice automatically
- **Audiobook-ready** — handles arbitrarily long text with near-constant VRAM via built-in chunking
- **Multilingual** — 600+ languages

## Installation

1. Clone into your ComfyUI custom nodes directory:
   ```bash
   cd ComfyUI/custom_nodes
   git clone https://github.com/ethanfel/ComfyUI-Omnivoice.git
   ```

2. Install dependencies **without overwriting ComfyUI's torch**:
   ```bash
   python install.py
   ```
   > **Warning:** Do NOT run `pip install omnivoice` directly — it pins `torch==2.8.*` from a CUDA 12.8 index and will overwrite ComfyUI's torch installation.

3. Restart ComfyUI. The nodes will appear under the **OmniVoice** category.

## Nodes

### OmniVoice Model Loader

Loads the OmniVoice model. Downloads automatically from HuggingFace on first run and caches locally.

| Input | Type | Description |
|-------|------|-------------|
| `model_source` | dropdown | `Auto-download (HuggingFace)` or `Local path` |
| `local_path` | string | Path to local checkpoint (optional) |
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
| `ref_text` | string | Transcription of ref audio — auto-detected if blank (optional) |
| `instruct` | string | Voice description for voice design mode (optional) |
| `speed` | float | Speed multiplier — default 1.0 |
| `num_step` | int | Diffusion steps — default 32 (use 16 for faster generation) |

**Output:** `AUDIO` at 24kHz — connects directly to ComfyUI's Save Audio node.

## Example Workflow (Audiobook)

```
[OmniVoice Model Loader] ─────────────────────────┐
                                                    ▼
[Load Audio (narrator clip)] ──► [OmniVoice Generate] ──► [Save Audio]
                                        ▲
                              text = "Page 1 content..."
                              mode = voice_cloning
```

Repeat the Generate + Save Audio nodes for each page, reusing the same loader.

## Credits

- [OmniVoice](https://github.com/k2-fsa/OmniVoice) by k2-fsa
- [OmniVoice paper](https://arxiv.org/abs/2604.00688)
