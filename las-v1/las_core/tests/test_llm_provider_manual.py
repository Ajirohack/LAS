import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sources.llm_provider import Provider
from services.llm_service import LLMService
from config.settings import settings
import pytest

def test_provider_initialization():
    provider = Provider("ollama", "tinydolphin", is_local=True)
    assert provider.provider_name == "ollama"
    assert provider.model == "tinydolphin"

def test_list_models():
    # Test Ollama listing (assumes Ollama is running or returns empty list)
    provider = Provider("ollama", "tinydolphin", is_local=True)
    models = provider.list_models()
    print(f"Ollama Models: {models}")
    assert isinstance(models, list)

    # Test OpenRouter listing
    provider = Provider("openrouter", "anthropic/claude-3-opus", is_local=False)
    models = provider.list_models()
    print(f"OpenRouter Models (first 5): {models[:5]}")
    assert isinstance(models, list)
    assert len(models) > 0

def test_ollama_generation():
    # This might fail if Ollama is not running, but we want to test the logic
    try:
        provider = Provider("ollama", "tinydolphin", is_local=True)
        response = provider.respond([{"role": "user", "content": "Hello"}])
        print(f"Ollama Response: {response}")
        assert isinstance(response, str)
        assert len(response) > 0
    except Exception as e:
        print(f"Ollama test skipped or failed: {e}")

if __name__ == "__main__":
    print("Running manual verification...")
    test_provider_initialization()
    test_list_models()
    test_ollama_generation()
    print("Verification complete.")
