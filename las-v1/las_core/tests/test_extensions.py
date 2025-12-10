import unittest
import os
from extensions.linux_desktop_extension import LinuxDesktopExtension
from extensions.browser_extension import BrowserExtension
from extensions.android_extension import AndroidExtension
import subprocess
import pathlib

class TestExtensions(unittest.TestCase):

    def tearDown(self):
        # Clean up created files
        if os.path.exists("test_screenshot.png"):
            os.remove("test_screenshot.png")
        if os.path.exists("tests/test.html"):
            os.remove("tests/test.html")

    def test_linux_desktop_screenshot(self):
        """
        Tests that the LinuxDesktopExtension can take a screenshot.
        """
        extension = LinuxDesktopExtension()
        filename = "test_screenshot.png"
        
        # Ensure the file doesn't exist before the test
        if os.path.exists(filename):
            os.remove(filename)
            
        result = extension.take_screenshot(filename)
        self.assertTrue(os.path.exists(filename))
        self.assertIn("Screenshot saved", result)
        
        # Clean up the file
        os.remove(filename)

    def test_browser_extension_init(self):
        """
        Tests that the BrowserExtension initializes without errors.
        """
        extension = BrowserExtension()
        self.assertIsNotNone(extension.browser)
        # Check that a browser process is running
        self.assertIsNotNone(extension.browser.driver.service.process)
        extension.__del__() # Explicitly close the browser

    def test_browser_browse_local_file(self):
        """
        Tests browsing a local HTML file.
        """
        # Create a dummy html file for testing
        html_content = """
        <!DOCTYPE html>
        <html><head><title>Test</title></head>
        <body><h1>Hello</h1><a href="https://google.com">Google</a></body></html>
        """
        with open("tests/test.html", "w") as f:
            f.write(html_content)

        extension = BrowserExtension()
        # Get absolute path to the file
        file_path = str(pathlib.Path("tests/test.html").resolve())
        
        result = extension.browse_website(f"file://{file_path}")
        self.assertIn("Hello", result)
        extension.__del__()

    def test_browser_get_navigable(self):
        """
        Tests getting navigable links from a local HTML file.
        """
        html_content = """
        <!DOCTYPE html>
        <html><head><title>Test</title></head>
        <body>
            <h1>Hello</h1>
            <a href="https://www.google.com">Google</a>
            <a href="https://www.openai.com">OpenAI</a>
            <a href="/local-link">A local link</a>
        </body></html>
        """
        with open("tests/test.html", "w") as f:
            f.write(html_content)

        extension = BrowserExtension()
        file_path = str(pathlib.Path("tests/test.html").resolve())
        extension.browse_website(f"file://{file_path}")
        
        links = extension.get_navigable()
        self.assertIn("https://www.google.com/", links)
        self.assertIn("https://www.openai.com/", links)
        self.assertNotIn("/local-link", links) # Should only include absolute URLs
        extension.__del__()

    @unittest.skipIf("ANDROID_SERIAL" not in os.environ, "No Android device configured for testing (set ANDROID_SERIAL env var)")
    def test_android_extension_list_devices(self):
        """
        Tests that the AndroidExtension can list devices.
        Requires a connected device and ANDROID_SERIAL environment variable.
        """
        extension = AndroidExtension()
        device_id = os.environ["ANDROID_SERIAL"]
        result = extension.android_list_devices()
        self.assertIn(device_id, result)

    @unittest.skipIf("ANDROID_SERIAL" not in os.environ, "No Android device configured for testing (set ANDROID_SERIAL env var)")
    def test_android_shell_echo(self):
        """
        Tests the android_shell command with a simple echo.
        """
        extension = AndroidExtension()
        device_id = os.environ["ANDROID_SERIAL"]
        test_string = "hello_android"
        result = extension.android_shell(device_id, f"echo {test_string}")
        self.assertIn(test_string, result)


if __name__ == "__main__":
    unittest.main()
