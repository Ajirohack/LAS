import pyautogui
from sdk.decorators import command
from typing import Optional

class LinuxDesktopExtension:
    def __init__(self):
        """
        Initializes the LinuxDesktopExtension.
        """
        # PyAutoGUI can fail on headless systems, so we need to handle that.
        try:
            pyautogui.FAILSAFE = True
        except Exception as e:
            print(f"Warning: Failed to initialize pyautogui. GUI automation may not work. Error: {e}")

    @command(
        description="Moves the mouse to the specified coordinates on the screen.",
        arguments={
            "x": "The x-coordinate to move the mouse to.",
            "y": "The y-coordinate to move the mouse to.",
            "duration": "Optional. The time in seconds to take to move the mouse. Defaults to 0.5."
        }
    )
    def mouse_move(self, x: int, y: int, duration: float = 0.5) -> str:
        """
        Moves the mouse to the specified coordinates.
        """
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
            "button": "Optional. The mouse button to click: 'left', 'right', or 'middle'. Defaults to 'left'."
        }
    )
    def mouse_click(self, x: Optional[int] = None, y: Optional[int] = None, button: str = 'left') -> str:
        """
        Clicks the mouse at the specified coordinates.
        """
        try:
            pyautogui.click(x=x, y=y, button=button)
            return f"{button.capitalize()} click at ({x}, {y}) successful."
        except Exception as e:
            return f"Error clicking mouse: {e}"

    @command(
        description="Types the specified text using the keyboard.",
        arguments={"text": "The text to type."}
    )
    def keyboard_type(self, text: str) -> str:
        """
        Types the given text.
        """
        try:
            pyautogui.write(text)
            return f"Typed text: '{text}'"
        except Exception as e:
            return f"Error typing text: {e}"

    @command(
        description="Takes a screenshot of the entire screen and saves it to a file.",
        arguments={"filename": "The path to save the screenshot to. E.g., 'screenshot.png'."}
    )
    def take_screenshot(self, filename: str) -> str:
        """
        Takes a screenshot and saves it to a file.
        """
        try:
            pyautogui.screenshot(filename)
            return f"Screenshot saved to {filename}"
        except Exception as e:
            return f"Error taking screenshot: {e}"
