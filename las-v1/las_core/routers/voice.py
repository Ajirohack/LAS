from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import tempfile
import os

from services.whisper_stt import get_whisper_service
from services.tts_service import get_tts_service
from services.vision_service import get_vision_service

router = APIRouter()

class TranscriptionRequest(BaseModel):
    language: Optional[str] = None
    model_size: Optional[str] = "base"

class SynthesisRequest(BaseModel):
    text: str
    voice_id: Optional[str] = None
    rate: int = 150

class VisionRequest(BaseModel):
    prompt: Optional[str] = "Describe this image in detail"

@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: Optional[str] = None,
    model_size: str = "base"
):
    """Transcribe audio file using Whisper."""
    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            # Transcribe
            stt_service = get_whisper_service(model_size=model_size)
            result = stt_service.transcribe_file(tmp_path, language=language)
            return result
        finally:
            # Clean up
            try:
                os.unlink(tmp_path)
            except:
                pass
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@router.post("/synthesize")
async def synthesize_speech(request: SynthesisRequest):
    """Synthesize speech from text."""
    try:
        tts_service = get_tts_service()
        
        # Generate audio to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            output_path = tmp_file.name
        
        success = tts_service.synthesize_to_file(
            text=request.text,
            output_path=output_path,
            voice_id=request.voice_id,
            rate=request.rate
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Speech synthesis failed")
        
        # Return audio file
        return FileResponse(
            output_path,
            media_type="audio/wav",
            filename="speech.wav"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Synthesis failed: {str(e)}")

@router.get("/voices")
async def list_voices():
    """List available TTS voices."""
    try:
        tts_service = get_tts_service()
        voices = tts_service.get_voices()
        return {"voices": voices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list voices: {str(e)}")

@router.post("/vision/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    prompt: str = Form("Describe this image in detail")
):
    """Analyze an image using vision-capable LLM."""
    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            # Analyze
            vision_service = get_vision_service()
            result = vision_service.analyze_image(tmp_path, prompt=prompt)
            return {"analysis": result}
        finally:
            # Clean up
            try:
                os.unlink(tmp_path)
            except:
                pass
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vision analysis failed: {str(e)}")

@router.post("/vision/extract-text")
async def extract_text_from_image(file: UploadFile = File(...)):
    """Extract text from an image (OCR)."""
    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            # Extract text
            vision_service = get_vision_service()
            result = vision_service.extract_text(tmp_path)
            return {"text": result}
        finally:
            # Clean up
            try:
                os.unlink(tmp_path)
            except:
                pass
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {str(e)}")

class RecordRequest(BaseModel):
    duration: int = 5
    prompt: str = "Analyze what is happening on the screen."

@router.post("/vision/record-and-analyze")
async def record_and_analyze(request: RecordRequest):
    """Record screen and analyze it."""
    try:
        vision_service = get_vision_service()
        
        # Record
        video_path = vision_service.record_screen(duration=request.duration)
        
        if not os.path.exists(video_path):
            raise HTTPException(status_code=500, detail="Recording failed to save file.")
            
        # Analyze
        analysis = vision_service.analyze_video(video_path, prompt=request.prompt)
        
        return {
            "video_path": video_path,
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Screen analysis failed: {str(e)}")

@router.post("/vision/analyze-video")
async def analyze_uploaded_video(
    file: UploadFile = File(...),
    prompt: str = Form("Analyze this video")
):
    """Analyze an uploaded video file."""
    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            # Analyze
            vision_service = get_vision_service()
            result = vision_service.analyze_video(tmp_path, prompt=prompt)
            return {"analysis": result}
        finally:
            # Clean up
            try:
                os.unlink(tmp_path)
            except:
                pass
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video analysis failed: {str(e)}")
