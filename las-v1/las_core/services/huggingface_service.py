"""
HuggingFace Hub Service - Comprehensive integration with HuggingFace Inference API.

Supports:
- Text generation (LLMs)
- Image generation (Stable Diffusion, FLUX)
- Audio processing (Whisper, TTS)
- Computer vision (image classification, object detection)
- Embeddings
- And more...
"""

from typing import Dict, Any, Optional, List
import os
from pathlib import Path
import base64
import requests
from huggingface_hub import InferenceClient, HfApi, list_models
from dotenv import load_dotenv

load_dotenv()

class HuggingFaceService:
    """Service for interacting with HuggingFace Inference API and Hub."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize HuggingFace service.
        
        Args:
            api_key: HuggingFace API key (or from HUGGINGFACE_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
        if not self.api_key:
            raise ValueError("HuggingFace API key not found. Set HUGGINGFACE_API_KEY env variable.")
        
        self.client = InferenceClient(token=self.api_key)
        self.api = HfApi(token=self.api_key)
        self.base_url = "https://api-inference.huggingface.co/models"
    
    # ===== TEXT GENERATION =====
    
    def chat_completion(self, messages: List[Dict[str, str]], 
                       model: str = "meta-llama/Llama-3.3-70B-Instruct",
                       max_tokens: int = 1024,
                       temperature: float = 0.7,
                       stream: bool = False) -> Any:
        """
        Chat completion using HuggingFace models.
        
        Args:
            messages: Chat messages in OpenAI format
            model: Model ID from HuggingFace Hub
            max_tokens: Max tokens to generate
            temperature: Sampling temperature
            stream: Whether to stream the response
        """
        try:
            if stream:
                return self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=True
                )
            else:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Chat completion failed: {e}")
    
    def text_generation(self, prompt: str, 
                       model: str = "meta-llama/Llama-3.3-70B-Instruct",
                       max_new_tokens: int = 512) -> str:
        """
        Generate text from a prompt.
        
        Args:
            prompt: Input prompt
            model: Model ID
            max_new_tokens: Maximum tokens to generate
        """
        try:
            response = self.client.text_generation(
                prompt,
                model=model,
                max_new_tokens=max_new_tokens
            )
            return response
        except Exception as e:
            raise RuntimeError(f"Text generation failed: {e}")
    
    # ===== IMAGE GENERATION =====
    
    def text_to_image(self, prompt: str,
                     model: str = "stabilityai/stable-diffusion-3.5-large",
                     negative_prompt: Optional[str] = None,
                     save_path: Optional[str] = None) -> str:
        """
        Generate image from text prompt.
        
        Args:
            prompt: Text description
            model: Image generation model
            negative_prompt: What to avoid
            save_path: Where to save the image
        
        Returns:
            Path to saved image
        """
        try:
            image = self.client.text_to_image(
                prompt,
                model=model,
                negative_prompt=negative_prompt
            )
            
            if save_path is None:
                save_path = f".screenshots/generated_{int(time.time())}.png"
            
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            image.save(save_path)
            
            return save_path
        except Exception as e:
            raise RuntimeError(f"Image generation failed: {e}")
    
    def image_to_image(self, image_path: str, prompt: str,
                      model: str = "timbrooks/instruct-pix2pix") -> str:
        """
        Transform image based on text instruction.
        
        Args:
            image_path: Input image path
            prompt: Transformation instruction
            model: Image-to-image model
        """
        try:
            from PIL import Image
            import time
            
            with open(image_path, "rb") as img_file:
                image = Image.open(img_file)
                result = self.client.image_to_image(
                    image,
                    prompt=prompt,
                    model=model
                )
            
            save_path = f".screenshots/transformed_{int(time.time())}.png"
            result.save(save_path)
            return save_path
        except Exception as e:
            raise RuntimeError(f"Image transformation failed: {e}")
    
    # ===== AUDIO =====
    
    def speech_to_text(self, audio_path: str,
                      model: str = "openai/whisper-large-v3") -> str:
        """
        Transcribe audio to text.
        
        Args:
            audio_path: Path to audio file
            model: ASR model
        """
        try:
            with open(audio_path, "rb") as audio_file:
                result = self.client.automatic_speech_recognition(
                    audio_file.read(),
                    model=model
                )
            return result['text'] if isinstance(result, dict) else str(result)
        except Exception as e:
            raise RuntimeError(f"Speech-to-text failed: {e}")
    
    def text_to_speech(self, text: str, 
                      model: str = "espnet/kan-bayashi_ljspeech_vits",
                      save_path: Optional[str] = None) -> str:
        """
        Convert text to speech.
        
        Args:
            text: Input text
            model: TTS model
            save_path: Where to save audio
        """
        try:
            import time
            
            audio_bytes = self.client.text_to_speech(text, model=model)
            
            if save_path is None:
                save_path = f".screenshots/speech_{int(time.time())}.wav"
            
            with open(save_path, "wb") as f:
                f.write(audio_bytes)
            
            return save_path
        except Exception as e:
            raise RuntimeError(f"Text-to-speech failed: {e}")
    
    # ===== COMPUTER VISION =====
    
    def image_classification(self, image_path: str,
                            model: str = "google/vit-base-patch16-224") -> List[Dict]:
        """Classify image content."""
        try:
            with open(image_path, "rb") as img:
                result = self.client.image_classification(img.read(), model=model)
            return result
        except Exception as e:
            raise RuntimeError(f"Image classification failed: {e}")
    
    def object_detection(self, image_path: str,
                        model: str = "facebook/detr-resnet-50") -> List[Dict]:
        """Detect objects in image."""
        try:
            with open(image_path, "rb") as img:
                result = self.client.object_detection(img.read(), model=model)
            return result
        except Exception as e:
            raise RuntimeError(f"Object detection failed: {e}")
    
    # ===== EMBEDDINGS =====
    
    def feature_extraction(self, texts: List[str],
                          model: str = "sentence-transformers/all-MiniLM-L6-v2") -> List[List[float]]:
        """
        Generate embeddings for texts.
        
        Args:
            texts: List of text strings
            model: Embedding model
        """
        try:
            embeddings = self.client.feature_extraction(texts, model=model)
            return embeddings
        except Exception as e:
            raise RuntimeError(f"Feature extraction failed: {e}")
    
    # ===== MODEL DISCOVERY =====
    
    def search_models(self, 
                     task: Optional[str] = None,
                     library: Optional[str] = None,
                     limit: int = 20) -> List[Dict]:
        """
        Search HuggingFace Hub for models.
        
        Args:
            task: Filter by task (e.g., "text-generation", "image-generation")
            library: Filter by library (e.g., "transformers", "diffusers")
            limit: Max results
        """
        try:
            models = list(list_models(
                task=task,
                library=library,
                limit=limit,
                token=self.api_key
            ))
            
            return [{
                "id": model.id,
                "task": getattr(model, 'pipeline_tag', None),
                "downloads": getattr(model, 'downloads', 0),
                "likes": getattr(model, 'likes', 0)
            } for model in models]
        except Exception as e:
            raise RuntimeError(f"Model search failed: {e}")
    
    def get_model_info(self, model_id: str) -> Dict:
        """Get detailed information about a model."""
        try:
            info = self.api.model_info(model_id)
            return {
                "id": info.id,
                "task": getattr(info, 'pipeline_tag', None),
                "downloads": getattr(info, 'downloads', 0),
                "likes": getattr(info, 'likes', 0),
                "tags": getattr(info, 'tags', [])
            }
        except Exception as e:
            raise RuntimeError(f"Failed to get model info: {e}")

# Singleton instance
_hf_service: Optional[HuggingFaceService] = None

def get_huggingface_service() -> HuggingFaceService:
    """Get or create HuggingFaceService instance."""
    global _hf_service
    if _hf_service is None:
        _hf_service = HuggingFaceService()
    return _hf_service
