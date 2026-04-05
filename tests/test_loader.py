# tests/test_loader.py
from unittest.mock import patch, MagicMock
import pytest
from nodes.loader import OmniVoiceModelLoader


def test_input_types_structure():
    inputs = OmniVoiceModelLoader.INPUT_TYPES()
    required = inputs["required"]
    assert "device" in required
    assert "dtype" in required
    assert "optional" not in inputs or "local_path" not in inputs.get("optional", {})


def test_input_types_device_choices():
    inputs = OmniVoiceModelLoader.INPUT_TYPES()
    choices = inputs["required"]["device"][0]
    assert "cuda:0" in choices
    assert "cpu" in choices


def test_return_type():
    assert OmniVoiceModelLoader.RETURN_TYPES == ("OMNIVOICE_MODEL",)


def test_load_model():
    loader = OmniVoiceModelLoader()
    mock_model = MagicMock()
    with patch("nodes.loader.OmniVoice") as MockOmniVoice:
        MockOmniVoice.from_pretrained.return_value = mock_model
        result = loader.load_model(device="cpu", dtype="float32")
    assert result == (mock_model,)
    call_args = MockOmniVoice.from_pretrained.call_args
    assert call_args[0][0] == "k2-fsa/OmniVoice"


def test_load_model_dtype_mapped():
    import torch
    loader = OmniVoiceModelLoader()
    with patch("nodes.loader.OmniVoice") as MockOmniVoice:
        MockOmniVoice.from_pretrained.return_value = MagicMock()
        loader.load_model(device="cpu", dtype="float16")
    call_kwargs = MockOmniVoice.from_pretrained.call_args[1]
    assert call_kwargs["dtype"] == torch.float16
