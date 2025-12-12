"""
Linux Desktop Extension - GUI automation for Linux/macOS/Windows desktops.

Uses PyAutoGUI for cross-platform GUI automation including mouse control,
keyboard input, and screenshots.
"""

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    pyautogui = None
    PYAUTOGUI_AVAILABLE = False

from sdk.decorators import command
from typing import Optional, List
import os


class LinuxDesktopExtension:
    """
    Extension for desktop GUI automation using PyAutoGUI.
    
    Works on Linux, macOS, and Windows systems with a display.
    Note: Requires a display - will fail on headless systems.
    """
    
    def __init__(self):
        """Initializes the LinuxDesktopExtension."""
        try:
            if PYAUTOGUI_AVAILABLE:
                pyautogui.FAILSAFE = True  # Move mouse to corner to abort
                pyautogui.PAUSE = 0.1  # Small pause between actions
                self._available = True
            else:
                print("Warning: PyAutoGUI not installed. GUI automation disabled.")
                self._available = False
        except Exception as e:
            print(f"Warning: Failed to initialize pyautogui. GUI automation may not work. Error: {e}")
            self._available = False

    # ========== MOUSE COMMANDS ==========

    @command(
        description="Moves the mouse to the specified coordinates on the screen.",
        arguments={
            "x": "The x-coordinate to move the mouse to.",
            "y": "The y-coordinate to move the mouse to.",
            "duration": "Optional. The time in seconds to take to move the mouse. Defaults to 0.5."
        }
    )
    def mouse_move(self, x: int, y: int, duration: float = 0.5) -> str:
        """Moves the mouse to the specified coordinates."""
        if not PYAUTOGUI_AVAILABLE: return "Error: PyAutoGUI is not available."
        try:
            pyautogui.moveTo(x, y, duration=duration)
            return f"Mouse moved to ({x}, {y})."
        except Exception as e:
            return f"Error moving mouse: {e}"

    @command(
        description="Clicks the mouse at the specified coordinates.",
        arguments={
            "x": "Optional. The x-coordinate to click at. If not provided, clicks at the current position.",
            "y": "Optional. The y-coordinate to click at. If not provided, clicks at the current position.",
            "button": "Optional. The mouse button to click: 'left', 'right', or 'middle'. Defaults to 'left'.",
            "clicks": "Optional. Number of clicks. Defaults to 1. Use 2 for double-click."
        }
    )
    def mouse_click(self, x: Optional[int] = None, y: Optional[int] = None, 
                    button: str = 'left', clicks: int = 1) -> str:
        """Clicks the mouse at the specified coordinates."""
        if not PYAUTOGUI_AVAILABLE: return "Error: PyAutoGUI is not available."
        try:
            pyautogui.click(x=x, y=y, button=button, clicks=clicks)
            click_type = "Double-click" if clicks == 2 else f"{button.capitalize()} click"
            pos = f"({x}, {y})" if x is not None else "current position"
            return f"{click_type} at {pos} successful."
        except Exception as e:
            return f"Error clicking mouse: {e}"

    @command(
        description="Drags the mouse from one position to another.",
        arguments={
            "x": "The x-coordinate to drag to.",
            "y": "The y-coordinate to drag to.",
            "duration": "Optional. Time in seconds for the drag. Defaults to 0.5.",
            "button": "Optional. Mouse button to hold during drag. Defaults to 'left'."
        }
    )
    def mouse_drag(self, x: int, y: int, duration: float = 0.5, button: str = 'left') -> str:
        """Drags the mouse from current position to (x, y)."""
        if not PYAUTOGUI_AVAILABLE: return "Error: PyAutoGUI is not available."
        try:
            pyautogui.drag(x, y, duration=duration, button=button)
            return f"Dragged mouse to ({x}, {y})."
        except Exception as e:
            return f"Error dragging mouse: {e}"

    @command(
        description="Scrolls the mouse wheel.",
        arguments={
            "clicks": "Number of scroll clicks. Positive = up, negative = down.",
            "x": "Optional. X-coordinate to scroll at.",
            "y": "Optional. Y-coordinate to scroll at."
        }
    )
    def mouse_scroll(self, clicks: int, x: Optional[int] = None, y: Optional[int] = None) -> str:
        """Scrolls the mouse wheel."""
        if not PYAUTOGUI_AVAILABLE: return "Error: PyAutoGUI is not available."
        try:
            pyautogui.scroll(clicks, x=x, y=y)
            direction = "up" if clicks > 0 else "down"
            return f"Scrolled {direction} {abs(clicks)} clicks."
        except Exception as e:
            return f"Error scrolling: {e}"

    @command(description="Gets the current mouse position.")
    def mouse_position(self) -> str:
        """Returns the current mouse position."""
        if not PYAUTOGUI_AVAILABLE: return "Error: PyAutoGUI is not available."
        try:
            x, y = pyautogui.position()
            return f"Current mouse position: ({x}, {y})"
        except Exception as e:
            return f"Error getting mouse position: {e}"

    # ========== KEYBOARD COMMANDS ==========

    @command(
        description="Types the specified text using the keyboard.",
        arguments={
            "text": "The text to type.",
            "interval": "Optional. Seconds between each key press. Defaults to 0.0."
        }
    )
    def keyboard_type(self, text: str, interval: float = 0.0) -> str:
        """Types the given text."""
        if not PYAUTOGUI_AVAILABLE: return "Error: PyAutoGUI is not available."
        try:
            pyautogui.write(text, interval=interval)
            return f"Typed text: '{text}'"
        except Exception as e:
            return f"Error typing text: {e}"

    @command(
        description="Presses a single key or key combination.",
        arguments={
            "key": "The key to press (e.g., 'enter', 'tab', 'escape', 'f1', 'a')."
        }
    )
    def keyboard_press(self, key: str) -> str:
        """Presses a single key."""
        if not PYAUTOGUI_AVAILABLE: return "Error: PyAutoGUI is not available."
        try:
            pyautogui.press(key)
            return f"Pressed key: {key}"
        except Exception as e:
            return f"Error pressing key: {e}"

    @command(
        description="Presses a hotkey combination (e.g., Ctrl+C, Alt+Tab).",
        arguments={
            "keys": "List of keys to press together (e.g., ['ctrl', 'c'] or ['alt', 'tab'])."
        }
    )
    def keyboard_hotkey(self, keys: List[str]) -> str:
        """Presses a hotkey combination."""
        if not PYAUTOGUI_AVAILABLE: return "Error: PyAutoGUI is not available."
        try:
            pyautogui.hotkey(*keys)
            return f"Pressed hotkey: {'+'.join(keys)}"
        except Exception as e:
            return f"Error pressing hotkey: {e}"

    @command(
        description="Holds down a key.",
        arguments={"key": "The key to hold down."}
    )
    def keyboard_key_down(self, key: str) -> str:
        """Holds down a key."""
        if not PYAUTOGUI_AVAILABLE: return "Error: PyAutoGUI is not available."
        try:
            pyautogui.keyDown(key)
            return f"Key down: {key}"
        except Exception as e:
            return f"Error holding key: {e}"

    @command(
        description="Releases a held key.",
        arguments={"key": "The key to release."}
    )
    def keyboard_key_up(self, key: str) -> str:
        """Releases a held key."""
        if not PYAUTOGUI_AVAILABLE: return "Error: PyAutoGUI is not available."
        try:
            pyautogui.keyUp(key)
            return f"Key up: {key}"
        except Exception as e:
            return f"Error releasing key: {e}"

    # ========== SCREENSHOT COMMANDS ==========

    @command(
        description="Takes a screenshot of the entire screen and saves it to a file.",
        arguments={"filename": "The path to save the screenshot to. E.g., 'screenshot.png'."}
    )
    def take_screenshot(self, filename: str) -> str:
        """Takes a screenshot and saves it to a file."""
        if not PYAUTOGUI_AVAILABLE: return "Error: PyAutoGUI is not available."
        try:
            # Ensure directory exists
            dir_path = os.path.dirname(filename)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            
            pyautogui.screenshot(filename)
            return f"Screenshot saved to {filename}"
        except Exception as e:
            return f"Error taking screenshot: {e}"

    @command(
        description="Takes a screenshot of a specific region.",
        arguments={
            "filename": "The path to save the screenshot.",
            "x": "Left edge x-coordinate of the region.",
            "y": "Top edge y-coordinate of the region.",
            "width": "Width of the region.",
            "height": "Height of the region."
        }
    )
    def take_screenshot_region(self, filename: str, x: int, y: int, width: int, height: int) -> str:
        """Takes a screenshot of a specific region."""
        if not PYAUTOGUI_AVAILABLE: return "Error: PyAutoGUI is not available."
        try:
            dir_path = os.path.dirname(filename)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            
            pyautogui.screenshot(filename, region=(x, y, width, height))
            return f"Region screenshot saved to {filename}"
        except Exception as e:
            return f"Error taking region screenshot: {e}"

    # ========== SCREEN INFO ==========

    @command(description="Returns the screen size (width, height).")
    def get_screen_size(self) -> str:
        """Gets the screen dimensions."""
        if not PYAUTOGUI_AVAILABLE: return "Error: PyAutoGUI is not available."
        try:
            width, height = pyautogui.size()
            return f"Screen size: {width}x{height}"
        except Exception as e:
            return f"Error getting screen size: {e}"

    @command(
        description="Locates an image on the screen and returns its position.",
        arguments={
            "image_path": "Path to the image file to find on screen.",
            "confidence": "Optional. Match confidence (0.0-1.0). Requires opencv-python. Defaults to 0.8."
        }
    )
    def locate_on_screen(self, image_path: str, confidence: float = 0.8) -> str:
        """Locates an image on the screen."""
        if not PYAUTOGUI_AVAILABLE: return "Error: PyAutoGUI is not available."
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                return f"Image found at: x={location.left}, y={location.top}, width={location.width}, height={location.height}"
            else:
                return "Image not found on screen."
        except Exception as e:
            return f"Error locating image: {e}"

    @command(
        description="Locates an image on screen and clicks its center.",
        arguments={
            "image_path": "Path to the image file to find and click.",
            "confidence": "Optional. Match confidence (0.0-1.0). Defaults to 0.8."
        }
    )
    def click_image(self, image_path: str, confidence: float = 0.8) -> str:
        """Locates an image and clicks its center."""
        if not PYAUTOGUI_AVAILABLE: return "Error: PyAutoGUI is not available."
        try:
            location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
            if location:
                pyautogui.click(location)
                return f"Clicked image at ({location.x}, {location.y})"
            else:
                return "Image not found on screen - click failed."
        except Exception as e:
            return f"Error clicking image: {e}"

    # ========== WINDOW MANAGEMENT ==========

    @command(
        description="Gets a list of all open windows.",
        arguments={}
    )
    def list_windows(self) -> str:
        """Lists all open windows."""
        if not PYAUTOGUI_AVAILABLE: return "Error: PyAutoGUI is not available."
        try:
            windows = pyautogui.getAllWindows()
            if not windows:
                return "No windows found."
            
            result = []
            for w in windows:
                result.append(f"- {w.title} ({w.width}x{w.height}) at ({w.left}, {w.top})")
            return "\n".join(result)
        except Exception as e:
            return f"Error listing windows: {e}"

    @command(
        description="Activates (focuses) a window by its title.",
        arguments={"title": "The title (or partial title) of the window to activate."}
    )
    def activate_window(self, title: str) -> str:
        """Activates a window by title."""
        if not PYAUTOGUI_AVAILABLE: return "Error: PyAutoGUI is not available."
        try:
            windows = pyautogui.getWindowsWithTitle(title)
            if windows:
                windows[0].activate()
                return f"Activated window: {windows[0].title}"
            else:
                return f"No window found with title containing: {title}"
        except Exception as e:
            return f"Error activating window: {e}"
