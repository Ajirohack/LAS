from typing import Optional, List
import os

class TTSService:
    """
    Text-to-Speech service using pyttsx3 (lightweight, cross-platform).
    For production, consider Coqui TTS for better quality.
    """
    
    def __init__(self):
        """Initialize TTS engine."""
        self.engine = None
        self._initialized = False
    
    def _ensure_initialized(self):
        """Lazy load the TTS engine."""
        if not self._initialized:
            try:
                import pyttsx3
                self.engine = pyttsx3.init()
                self._initialized = True
                print("✓ TTS engine initialized")
            except ImportError:
                raise ImportError(
                    "pyttsx3 is not installed. Install with: pip install pyttsx3"
                )
            except Exception as e:
                raise RuntimeError(f"Failed to initialize TTS engine: {e}")
    
    def get_voices(self) -> List[dict]:
        """Get available voices."""
        self._ensure_initialized()
        voices = self.engine.getProperty('voices')
        return [
            {
                "id": voice.id,
                "name": voice.name,
                "languages": voice.languages if hasattr(voice, 'languages') else []
            }
            for voice in voices
        ]
    
    def synthesize_to_file(self, text: str, output_path: str,
                           voice_id: Optional[str] = None,
                           rate: int = 150) -> bool:
        """
        Synthesize text to audio file.
        
        Args:
            text: Text to synthesize
            output_path: Path to save audio file
            voice_id: Optional voice ID (from get_voices())
            rate: Speech rate (words per minute)
        
        Returns:
            Success boolean
        """
        self._ensure_initialized()
        
        try:
            # Set voice if specified
            if voice_id:
                self.engine.setProperty('voice', voice_id)
            
            # Set speech rate
            self.engine.setProperty('rate', rate)
            
            # Save to file
            self.engine.save_to_file(text, output_path)
            self.engine.runAndWait()
            
            return os.path.exists(output_path)
        except Exception as e:
            print(f"TTS synthesis failed: {e}")
            return False
    
    def speak(self, text: str, voice_id: Optional[str] = None, rate: int = 150):
        """
        Speak text immediately (blocking).
        
        Args:
            text: Text to speak
            voice_id: Optional voice ID
            rate: Speech rate
        """
        self._ensure_initialized()
        
        try:
            if voice_id:
                self.engine.setProperty('voice', voice_id)
            self.engine.setProperty('rate', rate)
            
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"TTS speak failed: {e}")

# Create singleton instance
_tts_service: Optional[TTSService] = None

def get_tts_service() -> TTSService:
    """Get or create TTS service instance."""
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service
