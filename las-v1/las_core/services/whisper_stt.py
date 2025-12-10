import os
import tempfile
from pathlib import Path
from typing import Optional

class WhisperSTTService:
    """
    Speech-to-Text service using OpenAI Whisper.
    Supports local inference for privacy-preserving transcription.
    """
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper STT service.
        
        Args:
            model_size: Model size (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.model = None
        self._initialized = False
    
    def _ensure_initialized(self):
        """Lazy load the Whisper model."""
        if not self._initialized:
            try:
                import whisper
                print(f"Loading Whisper model: {self.model_size}")
                self.model = whisper.load_model(self.model_size)
                self._initialized = True
                print(f"✓ Whisper {self.model_size} model loaded")
            except ImportError:
                raise ImportError(
                    "Whisper is not installed. Install with: pip install openai-whisper"
                )
            except Exception as e:
                raise RuntimeError(f"Failed to load Whisper model: {e}")
    
    def transcribe_file(self, audio_path: str, language: Optional[str] = None) -> dict:
        """
        Transcribe an audio file.
        
        Args:
            audio_path: Path to audio file
            language: Optional language code (e.g., 'en', 'es')
        
        Returns:
            Dict with 'text' and 'segments' keys
        """
        self._ensure_initialized()
        
        try:
            result = self.model.transcribe(
                audio_path,
                language=language,
                fp16=False  # Use FP32 for better compatibility
            )
            
            return {
                "text": result["text"].strip(),
                "language": result.get("language", language),
                "segments": [
                    {
                        "start": seg["start"],
                        "end": seg["end"],
                        "text": seg["text"].strip()
                    }
                    for seg in result.get("segments", [])
                ]
            }
        except Exception as e:
            raise RuntimeError(f"Transcription failed: {e}")
    
    def transcribe_bytes(self, audio_bytes: bytes, format: str = "wav",
                         language: Optional[str] = None) -> dict:
        """
        Transcribe audio from bytes.
        
        Args:
            audio_bytes: Audio data as bytes
            format: Audio format (wav, mp3, etc.)
            language: Optional language code
        
        Returns:
            Dict with transcription results
        """
        # Save to temp file and transcribe
        with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        try:
            result = self.transcribe_file(tmp_path, language=language)
            return result
        finally:
            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except:
                pass

# Create singleton instance
_whisper_service: Optional[WhisperSTTService] = None

def get_whisper_service(model_size: str = "base") -> WhisperSTTService:
    """Get or create Whisper STT service instance."""
    global _whisper_service
    if _whisper_service is None or _whisper_service.model_size != model_size:
        _whisper_service = WhisperSTTService(model_size=model_size)
    return _whisper_service
