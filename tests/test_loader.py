# tests/test_loader.py
from unittest.mock import patch, MagicMock
import torch
import pytest
from nodes.loader import OmniVoiceModelLoader


def test_input_types_structure():
    inputs = OmniVoiceModelLoader.INPUT_TYPES()
    required = inputs["required"]
    assert "model_source" in required
    assert "device" in required
    assert "dtype" in required
    optional = inputs.get("optional", {})
    assert "local_path" in optional


def test_input_types_model_source_choices():
    inputs = OmniVoiceModelLoader.INPUT_TYPES()
    choices = inputs["required"]["model_source"][0]
    assert "Auto-download (HuggingFace)" in choices
    assert "Local path" in choices


def test_return_type():
    assert OmniVoiceModelLoader.RETURN_TYPES == ("OMNIVOICE_MODEL",)


def test_load_model_auto_download():
    loader = OmniVoiceModelLoader()
    mock_model = MagicMock()
    with patch("nodes.loader.OmniVoice") as MockOmniVoice:
        MockOmniVoice.from_pretrained.return_value = mock_model
        result = loader.load_model(
            model_source="Auto-download (HuggingFace)",
            device="cpu",
            dtype="float32",
            local_path="",
        )
    assert result == (mock_model,)
    MockOmniVoice.from_pretrained.assert_called_once()
    call_kwargs = MockOmniVoice.from_pretrained.call_args
    assert call_kwargs[0][0] == "k2-fsa/OmniVoice"


def test_load_model_local_path():
    loader = OmniVoiceModelLoader()
    mock_model = MagicMock()
    with patch("nodes.loader.OmniVoice") as MockOmniVoice:
        MockOmniVoice.from_pretrained.return_value = mock_model
        result = loader.load_model(
            model_source="Local path",
            device="cpu",
            dtype="float32",
            local_path="/some/local/path",
        )
    assert result == (mock_model,)
    call_args = MockOmniVoice.from_pretrained.call_args[0][0]
    assert call_args == "/some/local/path"
