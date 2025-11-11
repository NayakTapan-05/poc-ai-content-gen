"""
Tests for model selection and configuration.
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import config
import torch


def test_gpu_detection():
    """Test 1: GPU detection works."""
    gpu_available = torch.cuda.is_available()
    print(f"✓ Test 1 passed: GPU detection works (GPU available: {gpu_available})")


def test_model_configuration():
    """Test 2: Model configuration is loaded."""
    assert config.IMAGE_MODEL is not None
    assert config.VIDEO_MODEL is not None
    assert config.EMBEDDINGS_MODEL is not None
    
    print(f"✓ Test 2 passed: Model configuration loaded")
    print(f"  - Image model: {config.IMAGE_MODEL}")
    print(f"  - Video model: {config.VIDEO_MODEL}")
    print(f"  - Embeddings model: {config.EMBEDDINGS_MODEL}")


def test_image_model_options():
    """Test 3: Image model options are valid."""
    valid_models = ["sd-turbo", "sd15", "onnx", "sd-onnx"]
    
    assert config.IMAGE_MODEL in valid_models or config.IMAGE_MODEL.startswith("stabilityai/") or config.IMAGE_MODEL.startswith("runwayml/")
    
    print(f"✓ Test 3 passed: Image model option is valid ({config.IMAGE_MODEL})")


def test_video_model_options():
    """Test 4: Video model options are valid."""
    valid_models = ["svd-xt", "svd", "stable-video-diffusion-img2vid-xt"]
    
    assert config.VIDEO_MODEL in valid_models or config.VIDEO_MODEL.startswith("stabilityai/")
    
    print(f"✓ Test 4 passed: Video model option is valid ({config.VIDEO_MODEL})")


def test_generation_settings():
    """Test 5: Generation settings are configured."""
    assert config.IMAGE_SIZE > 0
    assert config.IMAGE_STEPS > 0
    assert config.VIDEO_FRAMES > 0
    assert config.VIDEO_STEPS > 0
    
    print(f"✓ Test 5 passed: Generation settings configured")
    print(f"  - Image: {config.IMAGE_SIZE}x{config.IMAGE_SIZE}, {config.IMAGE_STEPS} steps")
    print(f"  - Video: {config.VIDEO_RES}p, {config.VIDEO_FRAMES} frames, {config.VIDEO_STEPS} steps")


if __name__ == "__main__":
    test_gpu_detection()
    test_model_configuration()
    test_image_model_options()
    test_video_model_options()
    test_generation_settings()
    print("\n✅ All model configuration tests passed!")
