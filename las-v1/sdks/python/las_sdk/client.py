"""
LAS Python SDK

Programmatic access to Local Agent System API.

Usage:
    from las_sdk import LASClient
    
    client = LASClient("http://localhost:7777")
    response = client.query("What is quantum computing?")
    print(response["answer"])
"""

import requests
from typing import Dict, List, Optional, Any
import json

class LASClient:
    """Client for interacting with LAS API."""
    
    def __init__(self, base_url: str = "http://localhost:7777"):
        """Initialize LAS client.
        
        Args:
            base_url: Base URL of LAS API
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def query(self, text: str, provider: Optional[str] = None, 
              model: Optional[str] = None) -> Dict[str, Any]:
        """Send a query to the agent.
        
        Args:
            text: Query text
            provider: Optional LLM provider (ollama, openrouter, etc.)
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
    
    def list_skills(self) -> List[str]:
        """List all saved skills."""
        url = f"{self.base_url}/api/memory/skills"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()["skills"]
    
    def get_skill(self, name: str) -> Dict[str, Any]:
        """Get skill details.
        
        Args:
            name: Skill name
        
        Returns:
            Skill data
        """
        url = f"{self.base_url}/api/memory/skills/{name}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def list_reflections(self, task_type: Optional[str] = None, 
                         limit: int = 10) -> List[Dict[str, Any]]:
        """List reflections.
        
        Args:
            task_type: Optional filter by task type
            limit: Maximum results
        
        Returns:
            List of reflections
        """
        url = f"{self.base_url}/api/memory/reflections"
        params = {"limit": limit}
        if task_type:
            params["task_type"] = task_type
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()["reflections"]
    
    def get_lessons(self, task_description: str, limit: int = 5) -> List[str]:
        """Get relevant lessons for a task.
        
        Args:
            task_description: Task description
            limit: Maximum results
        
        Returns:
            List of lessons
        """
        url = f"{self.base_url}/api/memory/lessons/{task_description}"
        params = {"limit": limit}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()["lessons"]
    
    def transcribe(self, audio_file: str, language: Optional[str] = None,
                   model_size: str = "base") -> Dict[str, Any]:
        """Transcribe audio file.
        
        Args:
            audio_file: Path to audio file
            language: Optional language code
            model_size: Whisper model size
        
        Returns:
            Transcription result
        """
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
        """Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            voice_id: Optional voice ID
            rate: Speech rate
            output_file: Optional path to save audio
        
        Returns:
            Audio bytes
        """
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
        """Analyze image with vision model.
        
        Args:
            image_file: Path to image
            prompt: Analysis prompt
        
        Returns:
            Analysis text
        """
        url = f"{self.base_url}/api/voice/vision/analyze"
        
        with open(image_file, 'rb') as f:
            files = {'file': f}
            data = {'prompt': prompt}
            response = self.session.post(url, files=files, data=data)
        
        response.raise_for_status()
        return response.json()["analysis"]
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all plugins."""
        url = f"{self.base_url}/api/plugins"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()["plugins"]
    
    def load_plugin(self, name: str) -> Dict[str, str]:
        """Load a plugin.
        
        Args:
            name: Plugin name
        
        Returns:
            Status dict
        """
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
