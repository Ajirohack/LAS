import cv2
import numpy as np
import mss
import threading
import time
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

class ScreenRecorder:
    """
    Records screen activity to a video file.
    Uses mss for fast screen capture and OpenCV for video encoding.
    """
    
    def __init__(self, output_dir: str = ".screenshots/recordings"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.is_recording = False
        self.thread = None
        self.current_video_path = None
        self.stop_event = threading.Event()
        
    def start_recording(self, duration: Optional[int] = None) -> str:
        """
        Start recording the screen.
        
        Args:
            duration: Optional duration in seconds. If None, records until stop() is called.
            
        Returns:
            Path to the output video file.
        """
        if self.is_recording:
            raise RuntimeError("Recording is already in progress")
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.mp4"
        self.current_video_path = str(self.output_dir / filename)
        
        self.stop_event.clear()
        self.is_recording = True
        
        self.thread = threading.Thread(target=self._record_loop, args=(duration,))
        self.thread.start()
        
        return self.current_video_path
        
    def stop_recording(self) -> str:
        """
        Stop the current recording.
        
        Returns:
            Path to the saved video file.
        """
        if not self.is_recording:
            return ""
            
        self.stop_event.set()
        if self.thread:
            self.thread.join()
            
        self.is_recording = False
        return self.current_video_path
        
    def _record_loop(self, duration: Optional[int]):
        """Internal recording loop."""
        with mss.mss() as sct:
            # Get the primary monitor
            monitor = sct.monitors[1]
            width = monitor["width"]
            height = monitor["height"]
            
            # Define codec and create VideoWriter object
            # mp4v is widely supported
            fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
            out = cv2.VideoWriter(self.current_video_path, fourcc, 20.0, (width, height))
            
            start_time = time.time()
            
            try:
                while not self.stop_event.is_set():
                    if duration and (time.time() - start_time > duration):
                        break
                        
                    # Capture screen
                    img = sct.grab(monitor)
                    
                    # Convert to numpy array
                    frame = np.array(img)
                    
                    # Convert BGRA to BGR (OpenCV expects BGR)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    
                    # Write frame
                    out.write(frame)
                    
                    # Limit frame rate (approx 20 fps)
                    time.sleep(0.05)
                    
            except Exception as e:
                print(f"Recording error: {e}")
            finally:
                out.release()
                self.is_recording = False

    def capture_screenshot(self) -> str:
        """Capture a single screenshot."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        output_path = str(self.output_dir.parent / filename)
        
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            mss.tools.to_png(sct.grab(monitor).rgb, sct.grab(monitor).size, output=output_path)
            
        return output_path

# Singleton instance
_recorder: Optional[ScreenRecorder] = None

def get_screen_recorder() -> ScreenRecorder:
    global _recorder
    if _recorder is None:
        _recorder = ScreenRecorder()
    return _recorder
