from typing import Optional, List, Dict, Any
import base64
from pathlib import Path

class VisionService:
    """
    Vision service for analyzing images using vision-capable LLMs.
    Supports GPT-4V, Gemini Pro Vision, and other multimodal models.
    """
    
    def __init__(self):
        """Initialize vision service."""
        from services.llm_service import get_llm_service
        self.llm_service = get_llm_service()
    
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_image(self, image_path: str, prompt: str = "Describe this image in detail") -> str:
        """
        Analyze an image using a vision-capable LLM.
        
        Args:
            image_path: Path to image file
            prompt: Analysis prompt
        
        Returns:
            Analysis text
        """
        try:
            # Check if current provider supports vision
            provider = self.llm_service.provider
            provider_name = provider.provider_name
            
            if provider_name in ["gemini", "openai"]:
                return self._analyze_with_langchain(image_path, prompt)
            else:
                return f"Vision analysis not supported for provider: {provider_name}. Use 'gemini' or 'openai'."
        
        except Exception as e:
            return f"Vision analysis failed: {str(e)}"
    
    def _analyze_with_langchain(self, image_path: str, prompt: str) -> str:
        """Analyze image using LangChain multimodal models."""
        try:
            from langchain_core.messages import HumanMessage
            
            # Encode image
            image_data = self.encode_image(image_path)
            
            # Create multimodal message
            llm = self.llm_service.get_langchain_llm()
            
            # Different providers have different formats
            provider_name = self.llm_service.provider.provider_name
            
            if provider_name == "gemini":
                # Gemini format
                message = HumanMessage(
                    content=[
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_data}"}
                    ]
                )
            else:
                # OpenAI/GPT-4V format
                message = HumanMessage(
                    content=[
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                        }
                    ]
                )
            
            response = llm.invoke([message])
            return response.content
        
        except Exception as e:
            raise RuntimeError(f"Image analysis failed: {e}")
    
    def extract_text(self, image_path: str) -> str:
        """Extract text from an image (OCR)."""
        return self.analyze_image(
            image_path,
            prompt="Extract all text from this image. Return only the extracted text, nothing else."
        )
    
    def describe_for_context(self, image_path: str) -> str:
        """Generate a contextual description for agents."""
        return self.analyze_image(
            image_path,
            prompt="Describe this image in a way that would help an AI assistant understand the context. Focus on key elements, text, and purpose."
        )
    def analyze_video(self, video_path: str, prompt: str = "Analyze this video", num_frames: int = 5) -> str:
        """
        Analyze a video by extracting frames and sending them to the LLM.
        """
        import cv2
        import numpy as np
        
        frames = []
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames <= 0:
            return "Could not read video file."
            
        # Calculate indices for evenly spaced frames
        indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
        
        for i in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if ret:
                # Convert to base64
                _, buffer = cv2.imencode('.jpg', frame)
                b64_frame = base64.b64encode(buffer).decode('utf-8')
                frames.append(b64_frame)
                
        cap.release()
        
        if not frames:
            return "No frames extracted from video."
            
        return self._analyze_frames_with_langchain(frames, prompt)

    def _analyze_frames_with_langchain(self, frames: List[str], prompt: str) -> str:
        """Analyze multiple frames using LangChain."""
        try:
            from langchain_core.messages import HumanMessage
            
            content = [{"type": "text", "text": prompt}]
            
            # Add images
            for frame in frames:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{frame}"}
                })
            
            message = HumanMessage(content=content)
            llm = self.llm_service.get_langchain_llm()
            
            response = llm.invoke([message])
            return response.content
        except Exception as e:
            return f"Video analysis failed: {str(e)}"

    def record_screen(self, duration: int = 5) -> str:
        """Record screen for a specific duration and return path."""
        from services.screen_recorder import get_screen_recorder
        recorder = get_screen_recorder()
        path = recorder.start_recording(duration=duration)
        # If duration is set, we wait? Or let it run?
        # For simplicity in this synchronous method, we wait.
        import time
        time.sleep(duration + 1) # Wait for thread to finish
        return path

# Create singleton instance
_vision_service: Optional[VisionService] = None

def get_vision_service() -> VisionService:
    """Get or create Vision service instance."""
    global _vision_service
    if _vision_service is None:
        _vision_service = VisionService()
    return _vision_service
