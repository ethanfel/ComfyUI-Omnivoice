# tests/test_generator.py
from unittest.mock import patch, MagicMock
import torch
import pytest
from nodes.generator import OmniVoiceGenerate


def make_mock_model(return_tensors=None):
    mock = MagicMock()
    if return_tensors is None:
        return_tensors = [torch.zeros(1, 24000)]  # 1 second of silence
    mock.generate.return_value = return_tensors
    return mock


def test_input_types_structure():
    inputs = OmniVoiceGenerate.INPUT_TYPES()
    required = inputs["required"]
    assert "model" in required
    assert "text" in required
    assert "mode" in required
    optional = inputs.get("optional", {})
    assert "ref_audio" in optional
    assert "ref_text" in optional
    assert "instruct" in optional
    assert "speed" in optional
    assert "num_step" in optional


def test_return_type():
    assert OmniVoiceGenerate.RETURN_TYPES == ("AUDIO",)


def test_generate_auto_voice():
    node = OmniVoiceGenerate()
    mock_model = make_mock_model()
    result = node.generate(
        model=mock_model,
        text="Hello world",
        mode="auto_voice",
        speed=1.0,
        num_step=32,
    )
    audio = result[0]
    assert "waveform" in audio
    assert "sample_rate" in audio
    assert audio["sample_rate"] == 24000
    mock_model.generate.assert_called_once_with(
        text="Hello world", speed=1.0, num_step=32
    )


def test_generate_voice_design():
    node = OmniVoiceGenerate()
    mock_model = make_mock_model()
    result = node.generate(
        model=mock_model,
        text="Hello world",
        mode="voice_design",
        instruct="female, low pitch",
        speed=1.0,
        num_step=32,
    )
    audio = result[0]
    assert audio["sample_rate"] == 24000
    mock_model.generate.assert_called_once_with(
        text="Hello world", instruct="female, low pitch", speed=1.0, num_step=32
    )


def test_generate_voice_cloning():
    node = OmniVoiceGenerate()
    mock_model = make_mock_model()
    # Simulate ComfyUI AUDIO input: waveform shape (batch, channels, samples)
    ref_waveform = torch.zeros(1, 1, 24000)
    ref_audio_input = {"waveform": ref_waveform, "sample_rate": 24000}

    with patch("nodes.generator.sf.write") as mock_write:
        result = node.generate(
            model=mock_model,
            text="Hello world",
            mode="voice_cloning",
            ref_audio=ref_audio_input,
            ref_text="reference text",
            speed=1.0,
            num_step=32,
        )

    assert mock_write.called
    call_kwargs = mock_model.generate.call_args[1]
    assert call_kwargs["ref_text"] == "reference text"
    assert "ref_audio" in call_kwargs


def test_voice_cloning_without_ref_audio_raises():
    node = OmniVoiceGenerate()
    mock_model = make_mock_model()
    with pytest.raises(ValueError, match="ref_audio"):
        node.generate(
            model=mock_model,
            text="Hello",
            mode="voice_cloning",
            speed=1.0,
            num_step=32,
        )


def test_voice_design_without_instruct_raises():
    node = OmniVoiceGenerate()
    mock_model = make_mock_model()
    with pytest.raises(ValueError, match="instruct"):
        node.generate(
            model=mock_model,
            text="Hello",
            mode="voice_design",
            speed=1.0,
            num_step=32,
        )


def test_output_waveform_shape():
    node = OmniVoiceGenerate()
    # Simulate two chunks returned by OmniVoice
    chunk1 = torch.zeros(1, 24000)
    chunk2 = torch.zeros(1, 12000)
    mock_model = make_mock_model(return_tensors=[chunk1, chunk2])
    result = node.generate(
        model=mock_model, text="Long text", mode="auto_voice", speed=1.0, num_step=32
    )
    waveform = result[0]["waveform"]
    # Shape must be (batch=1, channels=1, samples=36000)
    assert waveform.shape == (1, 1, 36000)
