"""
LAS Python SDK

Programmatic access to Local Agent System API.

Usage:
    from las_sdk import LASClient
    
    client = LASClient("http://localhost:7777")
    
    # Simple query
    response = client.query("What is quantum computing?")
    print(response["answer"])
    
    # Chat completion (OpenAI compatible)
    messages = [{"role": "user", "content": "Hello!"}]
    response = client.chat(messages, model="gpt-4", stream=False)
    print(response.choices[0].message.content)
"""

import requests
import json
from typing import Dict, List, Optional, Any, Union, Generator, Iterator

class LASClient:
    """Client for interacting with LAS API."""
    
    def __init__(self, base_url: str = "http://localhost:7777", api_key: Optional[str] = None):
        """Initialize LAS client.
        
        Args:
            base_url: Base URL of LAS API
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
    
    def query(self, text: str, provider: Optional[str] = None, 
              model: Optional[str] = None) -> Dict[str, Any]:
        """Send a query to the agent system (legacy endpoint).
        
        Args:
            text: Query text
            provider: Optional LLM provider
            model: Optional model name
        
        Returns:
            Query response dict
        """
        url = f"{self.base_url}/api/query"
        payload = {"query": text}
        
        if provider:
            payload["provider"] = provider
        if model:
            payload["model"] = model
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def chat(self, messages: List[Dict[str, str]], model: str = "gpt-3.5-turbo", 
             stream: bool = False, **kwargs) -> Union[Dict[str, Any], Iterator[Dict[str, Any]]]:
        """Send a chat completion request (LiteLLM / OpenAI compatible).
        
        Args:
            messages: List of message dicts (role, content)
            model: Model name
            stream: Whether to stream response
            **kwargs: Additional arguments (temperature, max_tokens, etc.)
            
        Returns:
            Response dict or Iterator of chunks if streaming
        """
        url = f"{self.base_url}/api/v1/litellm/chat/completions"
        payload = {
            "messages": messages,
            "model": model,
            "stream": stream,
            **kwargs
        }
        
        if stream:
            return self._stream_chat(url, payload)
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def _stream_chat(self, url: str, payload: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """Handle streaming chat response."""
        response = self.session.post(url, json=payload, stream=True)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]
                    if data == '[DONE]':
                        break
                    try:
                        yield json.loads(data)
                    except json.JSONDecodeError:
                        continue

    def list_models(self) -> List[str]:
        """List available models."""
        url = f"{self.base_url}/api/v1/litellm/models"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()["models"]

    def list_providers(self) -> List[str]:
        """List available providers."""
        url = f"{self.base_url}/api/v1/litellm/providers"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()["providers"]

    # --- Memory & Skills ---

    def list_skills(self) -> List[str]:
        """List all saved skills."""
        url = f"{self.base_url}/api/memory/skills"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json().get("skills", [])
    
    def get_skill(self, name: str) -> Dict[str, Any]:
        """Get skill details."""
        url = f"{self.base_url}/api/memory/skills/{name}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def list_reflections(self, task_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """List reflections."""
        url = f"{self.base_url}/api/memory/reflections"
        params = {"limit": limit}
        if task_type:
            params["task_type"] = task_type
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json().get("reflections", [])
    
    def get_lessons(self, task_description: str, limit: int = 5) -> List[str]:
        """Get relevant lessons for a task."""
        url = f"{self.base_url}/api/memory/lessons/{task_description}"
        params = {"limit": limit}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json().get("lessons", [])
    
    # --- Voice & Vision ---

    def transcribe(self, audio_file: str, language: Optional[str] = None,
                   model_size: str = "base") -> Dict[str, Any]:
        """Transcribe audio file."""
        url = f"{self.base_url}/api/voice/transcribe"
        with open(audio_file, 'rb') as f:
            files = {'file': f}
            data = {'model_size': model_size}
            if language:
                data['language'] = language
            response = self.session.post(url, files=files, data=data)
        response.raise_for_status()
        return response.json()
    
    def synthesize(self, text: str, voice_id: Optional[str] = None,
                   rate: int = 150, output_file: Optional[str] = None) -> bytes:
        """Synthesize speech from text."""
        url = f"{self.base_url}/api/voice/synthesize"
        payload = {"text": text, "rate": rate}
        if voice_id:
            payload["voice_id"] = voice_id
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        audio_data = response.content
        if output_file:
            with open(output_file, 'wb') as f:
                f.write(audio_data)
        return audio_data
    
    def analyze_image(self, image_file: str, prompt: str = "Describe this image") -> str:
        """Analyze image with vision model."""
        url = f"{self.base_url}/api/voice/vision/analyze"
        with open(image_file, 'rb') as f:
            files = {'file': f}
            data = {'prompt': prompt}
            response = self.session.post(url, files=files, data=data)
        response.raise_for_status()
        return response.json()["analysis"]
    
    # --- Plugins & Tools ---

    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all plugins."""
        url = f"{self.base_url}/api/plugins"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json().get("plugins", [])
    
    def load_plugin(self, name: str) -> Dict[str, str]:
        """Load a plugin."""
        url = f"{self.base_url}/api/plugins/load/{name}"
        response = self.session.post(url)
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health."""
        url = f"{self.base_url}/health"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
