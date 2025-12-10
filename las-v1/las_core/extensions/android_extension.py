import subprocess
import os
from config.settings import settings
from sdk.decorators import command
from typing import List

class AndroidExtension:
    def __init__(self):
        """
        Initializes the AndroidExtension.
        """
        pass

    def _adb_base_command(self, device_id: str = None) -> List[str]:
        """
        Constructs the base adb command with host and port if specified.
        """
        args = ["adb"]
        if settings.android_adb_host:
            args.extend(["-H", str(settings.android_adb_host)])
        if settings.android_adb_port:
            args.extend(["-P", str(settings.android_adb_port)])
        if device_id:
            args.extend(["-s", device_id])
        return args

    @command(description="Lists all connected Android devices.")
    def android_list_devices(self) -> str:
        """
        Lists all connected Android devices.
        """
        try:
            cmd = self._adb_base_command() + ["devices"]
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)
            return out.stdout
        except subprocess.CalledProcessError as e:
            return f"Error listing devices: {e.stderr}"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"

    @command(
        description="Executes a shell command on a specified Android device.",
        arguments={
            "device_id": "The ID of the target device.",
            "command": "The shell command to execute."
        }
    )
    def android_shell(self, device_id: str, command: str) -> str:
        """
        Executes a shell command on a device.
        """
        try:
            cmd = self._adb_base_command(device_id) + ["shell", command]
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=20, check=True)
            return out.stdout
        except subprocess.CalledProcessError as e:
            return f"Error executing shell command: {e.stderr}"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"

    @command(
        description="Takes a screenshot of a specified Android device.",
        arguments={"device_id": "The ID of the target device."}
    )
    def android_screenshot(self, device_id: str) -> str:
        """
        Takes a screenshot of a device.
        """
        try:
            tmp_path = "/sdcard/screen.png"
            # Take screenshot
            shell_cmd = self._adb_base_command(device_id) + ["shell", "screencap", "-p", tmp_path]
            subprocess.run(shell_cmd, capture_output=True, text=True, timeout=20, check=True)
            
            # Pull screenshot from device
            local_dir = ".screenshots"
            os.makedirs(local_dir, exist_ok=True)
            local_path = os.path.join(local_dir, f"android_{device_id}.png")
            pull_cmd = self._adb_base_command(device_id) + ["pull", tmp_path, local_path]
            subprocess.run(pull_cmd, capture_output=True, text=True, timeout=20, check=True)
            
            # Clean up screenshot on device
            cleanup_cmd = self._adb_base_command(device_id) + ["shell", "rm", tmp_path]
            subprocess.run(cleanup_cmd, capture_output=True, text=True, timeout=10)
            
            return f"Screenshot saved to {local_path}"
        except subprocess.CalledProcessError as e:
            return f"Error taking screenshot: {e.stderr}"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"

    @command(
        description="Taps a specific coordinate on the screen.",
        arguments={
            "device_id": "The ID of the target device.",
            "x": "The x-coordinate.",
            "y": "The y-coordinate."
        }
    )
    def android_tap(self, device_id: str, x: int, y: int) -> str:
        """
        Taps a point on the screen.
        """
        return self.android_shell(device_id, f"input tap {x} {y}")

    @command(
        description="Swipes from one point to another on the screen.",
        arguments={
            "device_id": "The ID of the target device.",
            "x1": "The starting x-coordinate.",
            "y1": "The starting y-coordinate.",
            "x2": "The ending x-coordinate.",
            "y2": "The ending y-coordinate.",
            "duration_ms": "The duration of the swipe in milliseconds."
        }
    )
    def android_swipe(self, device_id: str, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> str:
        """
        Swipes on the screen.
        """
        return self.android_shell(device_id, f"input swipe {x1} {y1} {x2} {y2} {duration_ms}")

    @command(
        description="Types the given text into the focused input field.",
        arguments={
            "device_id": "The ID of the target device.",
            "text": "The text to type. Note: this command does not handle spaces well; use multiple commands or 'android_press_key' for spaces."
        }
    )
    def android_type(self, device_id: str, text: str) -> str:
        """
        Types text.
        """
        escaped_text = text.replace(" ", "%s")
        return self.android_shell(device_id, f"input text '{escaped_text}'")

    @command(
        description="Presses a specific key code on the device.",
        arguments={
            "device_id": "The ID of the target device.",
            "key_code": "The key code to press (e.g., 'HOME', 'BACK', 'ENTER', 'SPACE')."
        }
    )
    def android_press_key(self, device_id: str, key_code: str) -> str:
        """
        Presses a key. For a list of key codes, see the Android developer documentation for KeyEvent.
        Examples: HOME, BACK, DPAD_UP, DPAD_DOWN, ENTER, SPACE, DEL.
        """
        return self.android_shell(device_id, f"input keyevent {key_code.upper()}")
