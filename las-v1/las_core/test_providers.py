#!/usr/bin/env python3
"""
Test script for Ollama, OpenRouter, and Gemini providers.

Tests:
1. Ollama Local (gpt-oss:20b-cloud via local server)
2. Ollama Cloud (gpt-oss:20b-cloud via ollama.com)
3. OpenRouter (google/gemma-2-27b-it:free)
4. Google Gemini (gemini-1.5-flash)
"""

import os
import sys

# Set API keys
os.environ["OLLAMA_API_KEY"] = "8e25f62a1afb49bfa57b20ede8270e85.j1l7L7JyauQIY6qLoePLcJc1"
os.environ["OPENROUTER_API_KEY"] = "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"
os.environ["GOOGLE_API_KEY"] = "AIzaSyAgvr-fJBl4Ra4B3Wjom7-H7Idsh1SMKls"

from sources.provider_factory import ProviderFactory
from sources.providers.base_provider import ProviderConfig
from langchain_core.messages import HumanMessage

def test_provider(provider_name: str, model: str, description: str):
    """Test a provider with a simple query."""
    print(f"\n{'='*70}")
    print(f"Testing: {description}")
    print(f"Provider: {provider_name} | Model: {model}")
    print('='*70)
    
    try:
        # Create provider
        provider = ProviderFactory.create(
            provider_name=provider_name,
            model=model
        )
        
        print(f"✓ Provider created: {provider}")
        
        # List models
        try:
            models = provider.list_models()
            print(f"✓ Available models: {len(models)} models")
            if models:
                print(f"  First 5: {models[:5]}")
        except Exception as e:
            print(f"⚠ Could not list models: {e}")
        
        # Get LangChain LLM
        llm = provider.get_langchain_llm()
        print(f"✓ LangChain LLM created: {type(llm).__name__}")
        
        # Test simple query
        print("\nSending test query: 'Say hello in one sentence.'")
        response = llm.invoke([HumanMessage(content="Say hello in one sentence.")])
        print(f"\n✓ Response: {response.content}")
        
        print(f"\n✅ {description} - PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ {description} - FAILED")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all provider tests."""
    print("\n" + "="*70)
    print("LAS Provider Integration Tests")
    print("="*70)
    
    results = {}
    
    # Test 1: Ollama Local
    results["Ollama Local"] = test_provider(
        provider_name="ollama",
        model="gpt-oss:20b-cloud",
        description="Ollama Local (gpt-oss:20b-cloud)"
    )
    
    # Test 2: Ollama Cloud
    # Note: For cloud, we need to ensure the provider detects it's a cloud model
    results["Ollama Cloud"] = test_provider(
        provider_name="ollama",
        model="gpt-oss:20b-cloud",
        description="Ollama Cloud (gpt-oss:20b-cloud via ollama.com)"
    )
    
    # Test 3: OpenRouter
    results["OpenRouter"] = test_provider(
        provider_name="openrouter",
        model="mistralai/mistral-7b-instruct:free",
        description="OpenRouter (mistralai/mistral-7b-instruct:free)"
    )
    
    # Test 4: Google Gemini
    results["Gemini"] = test_provider(
        provider_name="gemini",
        model="gemini-2.5-flash",  # Using latest available model
        description="Google Gemini (gemini-2.5-flash)"
    )
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name:20} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All provider tests PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
