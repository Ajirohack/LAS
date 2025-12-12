"""
Browser Extension with Privacy Cloak Integration.

This extension provides browser automation capabilities with advanced privacy features
including fingerprint randomization, network anonymization, and behavioral obfuscation.
"""

from sources.browser import Browser, create_driver
from config.settings import settings
from sdk.decorators import command
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class BrowserExtension:
    """
    Browser automation extension with integrated Privacy Cloak.
    
    Features:
    - Fingerprint randomization (canvas, WebGL, audio, fonts)
    - Network anonymization (Tor, VPN, Proxy support)
    - Behavioral obfuscation for human-like interactions
    - Session isolation and leak prevention
    - Stealth mode with undetected-chromedriver
    """
    
    def __init__(self, privacy_enabled: bool = True):
        """
        Initializes the BrowserExtension with optional privacy features.
        
        Args:
            privacy_enabled: Whether to enable Privacy Cloak features (default: True)
        """
        # Default stealth settings
        self.timezone = "Europe/Paris"
        self.resolution = (1920, 1080)
        self.proxy_server = settings.proxy_server
        
        # Privacy Cloak integration
        self.privacy_enabled = privacy_enabled
        self._privacy_engine = None
        self._fingerprint_profile = None
        self._injection_script = None
        
        # Initialize privacy components if enabled
        if self.privacy_enabled:
            self._initialize_privacy_engine()
        
        # Create browser instance
        self.browser = self._new_browser()

    def _initialize_privacy_engine(self):
        """Initialize the Privacy Cloak engine and components."""
        try:
            from privacy_cloak_browser.core.config import PrivacyConfig, FingerprintProfile
            from privacy_cloak_browser.fingerprint.randomizer import FingerprintRandomizer
            from privacy_cloak_browser.behavior.obfuscator import BehaviorObfuscator
            from privacy_cloak_browser.leaks.preventer import LeakPreventer
            
            # Create privacy configuration
            self._privacy_config = PrivacyConfig(
                randomize_canvas=True,
                randomize_webgl=True,
                randomize_audio=True,
                randomize_fonts=True,
                spoof_timezone=True,
                block_webrtc=True,
                block_plugin_enumeration=True,
                block_media_device_enumeration=True,
                randomize_battery_status=True,
            )
            
            # Generate fingerprint profile
            self._fingerprint_profile = FingerprintProfile.generate_random(
                target_platform=self._privacy_config.target_platform
            )
            
            # Initialize randomizer and get injection script
            self._fingerprint_randomizer = FingerprintRandomizer(self._privacy_config)
            self._injection_script = self._fingerprint_randomizer.get_injection_script(
                self._fingerprint_profile
            )
            
            # Initialize behavior obfuscator for human-like actions
            self._behavior_obfuscator = BehaviorObfuscator(self._privacy_config)
            
            # Initialize leak preventer
            self._leak_preventer = LeakPreventer(self._privacy_config)
            
            logger.info(f"Privacy Cloak initialized with fingerprint: {self._fingerprint_profile.user_agent[:50]}...")
            
        except ImportError as e:
            logger.warning(f"Privacy Cloak modules not available: {e}. Running without privacy features.")
            self.privacy_enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize Privacy Cloak: {e}")
            self.privacy_enabled = False

    def __del__(self):
        """Destructor to ensure the browser driver is quit properly."""
        try:
            self.browser.driver.quit()
        except:
            pass

    def _new_browser(self) -> Browser:
        """
        Creates a new browser instance with privacy enhancements.
        """
        # Build browser options
        driver_kwargs = {
            "headless": settings.headless_browser,
            "stealth_mode": settings.stealth_mode,
            "lang": settings.languages.split(' ')[0] if hasattr(settings, 'languages') else 'en',
            "timezone": self.timezone,
            "resolution": self.resolution,
            "proxy_server": self.proxy_server,
        }
        
        # Apply privacy cloak fingerprint settings
        if self.privacy_enabled and self._fingerprint_profile:
            # Override with privacy cloak settings
            driver_kwargs["lang"] = self._fingerprint_profile.language
            driver_kwargs["timezone"] = self._fingerprint_profile.timezone
            driver_kwargs["resolution"] = (
                self._fingerprint_profile.screen_width,
                self._fingerprint_profile.screen_height
            )
            
            # Custom user agent from fingerprint
            driver_kwargs["user_agent"] = self._fingerprint_profile.user_agent
            
            logger.info(f"Applied Privacy Cloak fingerprint to browser")
        
        driver = create_driver(**driver_kwargs)
        browser = Browser(driver)
        
        # Inject anti-fingerprinting scripts after driver is created
        if self.privacy_enabled and self._injection_script:
            self._inject_privacy_scripts(browser)
        
        return browser

    def _inject_privacy_scripts(self, browser: Browser):
        """Inject anti-fingerprinting JavaScript into the browser."""
        try:
            # Execute the fingerprint protection script
            browser.driver.execute_cdp_cmd(
                'Page.addScriptToEvaluateOnNewDocument',
                {'source': self._injection_script}
            )
            logger.info("✓ Privacy protection scripts injected")
        except Exception as e:
            logger.warning(f"Could not inject privacy scripts: {e}")
            # Fallback: try direct script execution
            try:
                browser.driver.execute_script(self._injection_script)
                logger.info("✓ Privacy scripts injected (fallback method)")
            except Exception as e2:
                logger.error(f"Failed to inject privacy scripts: {e2}")

    def _apply_behavioral_obfuscation(self, action_type: str):
        """Apply human-like timing and patterns to actions."""
        if self.privacy_enabled and self._behavior_obfuscator:
            try:
                # Add human-like delay
                delay = self._behavior_obfuscator.get_human_delay(action_type)
                import time
                time.sleep(delay)
            except Exception as e:
                logger.debug(f"Behavioral obfuscation skipped: {e}")

    @command(
        description="Configures the stealth settings for the browser and restarts it with the new settings.",
        arguments={
            "timezone": "Optional. The timezone to use, e.g., 'America/New_York'.",
            "resolution": "Optional. A tuple of (width, height) for the screen resolution, e.g., [1920, 1080].",
            "proxy_server": "Optional. The proxy server to use, e.g., 'http://user:pass@host:port'."
        }
    )
    def configure_stealth(self, timezone: Optional[str] = None, resolution: Optional[Tuple[int, int]] = None, proxy_server: Optional[str] = None) -> str:
        """Updates stealth settings and restarts the browser."""
        if timezone:
            self.timezone = timezone
        if resolution:
            self.resolution = tuple(resolution)
        if proxy_server:
            self.proxy_server = proxy_server
            
        try:
            self.browser.driver.quit()
        except:
            pass
        
        # Regenerate fingerprint if privacy is enabled
        if self.privacy_enabled:
            self._initialize_privacy_engine()
            
        self.browser = self._new_browser()
        return f"Browser restarted with new stealth settings: timezone={self.timezone}, resolution={self.resolution}, proxy_server={self.proxy_server}"

    @command(
        description="Rotates the browser's identity by generating a new fingerprint profile.",
        arguments={}
    )
    def rotate_identity(self) -> str:
        """Rotate to a completely new browser fingerprint identity."""
        if not self.privacy_enabled:
            return "Privacy Cloak not enabled. Cannot rotate identity."
        
        try:
            # Regenerate fingerprint
            self._initialize_privacy_engine()
            
            # Restart browser with new identity
            try:
                self.browser.driver.quit()
            except:
                pass
            
            self.browser = self._new_browser()
            
            return f"Identity rotated. New fingerprint: {self._fingerprint_profile.user_agent[:60]}..."
        except Exception as e:
            return f"Failed to rotate identity: {e}"

    @command(
        description="Verifies that privacy protections are active and no leaks are detected.",
        arguments={}
    )
    def verify_privacy(self) -> str:
        """Run privacy verification checks."""
        if not self.privacy_enabled:
            return "Privacy Cloak not enabled."
        
        results = []
        
        # Check fingerprint is randomized
        if self._fingerprint_profile:
            results.append(f"✓ Fingerprint: {self._fingerprint_profile.user_agent[:40]}...")
        
        # Check scripts are injected
        if self._injection_script:
            results.append("✓ Anti-fingerprinting scripts active")
        
        # Check WebRTC protection
        try:
            webrtc_test = self.browser.driver.execute_script(
                "return window.RTCPeerConnection === undefined || "
                "navigator.webdriver === undefined"
            )
            if webrtc_test:
                results.append("✓ WebRTC protection active")
            else:
                results.append("⚠ WebRTC protection may be incomplete")
        except:
            results.append("⚠ Could not verify WebRTC protection")
        
        # Check automation indicators
        try:
            webdriver_hidden = self.browser.driver.execute_script(
                "return navigator.webdriver === undefined"
            )
            if webdriver_hidden:
                results.append("✓ Automation indicators hidden")
            else:
                results.append("⚠ Automation indicators visible")
        except:
            results.append("⚠ Could not verify automation indicators")
        
        return "\n".join(results)

    @command(
        description="Navigates to a specified URL and returns the text content of the page.",
        arguments={"url": "The URL to browse to."}
    )
    def browse_website(self, url: str) -> str:
        """Navigates to a URL and returns the text content."""
        self._apply_behavioral_obfuscation("navigation")
        ok = self.browser.go_to(url)
        if not ok:
            return "Navigation failed."
        return self.browser.get_text() or "Page was empty or could not be read."

    @command(
        description="Sets the browser's geolocation for the current session.",
        arguments={
            "latitude": "The latitude for the geolocation.",
            "longitude": "The longitude for the geolocation.",
            "accuracy": "Optional accuracy in meters. Defaults to 100."
        }
    )
    def set_geolocation(self, latitude: float, longitude: float, accuracy: float = 100.0) -> str:
        """Sets the browser's geolocation."""
        ok = self.browser.set_geolocation(latitude, longitude, accuracy)
        return "Geolocation set successfully." if ok else "Failed to set geolocation."

    @command(
        description="Clicks an element on the page specified by its XPath.",
        arguments={"xpath": "The XPath of the element to click."}
    )
    def click_element(self, xpath: str) -> str:
        """Clicks an element specified by XPath."""
        self._apply_behavioral_obfuscation("click")
        ok = self.browser.click_element(xpath)
        return "Element clicked." if ok else "Failed to click element."

    @command(
        description="Fills a form on the current page with the provided data.",
        arguments={"input_list": "A list of strings, where each string is in the format '[input_name](value)'."}
    )
    def fill_form(self, input_list: List[str]) -> str:
        """Fills a form and submits it."""
        self._apply_behavioral_obfuscation("typing")
        ok = self.browser.fill_form(input_list)
        return "Form filled and submitted successfully." if ok else "Failed to fill or submit form."

    @command(description="Returns a list of all visible input fields on the current page.")
    def get_form_inputs(self) -> List[str]:
        """Gets all visible form inputs on the page."""
        return self.browser.get_form_inputs()

    @command(description="Returns the current URL of the browser.")
    def get_current_url(self) -> str:
        """Gets the current URL."""
        return self.browser.get_current_url()

    @command(description="Scrolls to the bottom of the current page.")
    def scroll_bottom(self) -> str:
        """Scrolls to the bottom of the page."""
        self._apply_behavioral_obfuscation("scroll")
        ok = self.browser.scroll_bottom()
        return "Scrolled to bottom." if ok else "Failed to scroll."

    @command(description="Takes a screenshot of the current page and returns the path to the image.")
    def screenshot(self) -> str:
        """Takes a screenshot of the page."""
        ok = self.browser.screenshot()
        return f"Screenshot saved to {self.browser.get_screenshot()}" if ok else "Failed to take screenshot."
        
    @command(description="Returns the text content of the current page.")
    def get_text(self) -> str:
        """Gets the text content of the current page."""
        return self.browser.get_text() or "Page was empty or could not be read."

    @command(description="Returns a list of all navigable links on the current page.")
    def get_navigable(self) -> List[str]:
        return self.browser.get_navigable()

    @command(description="Returns the current privacy status and fingerprint info.")
    def get_privacy_status(self) -> dict:
        """Get current privacy cloak status."""
        status = {
            "privacy_enabled": self.privacy_enabled,
            "fingerprint_active": self._fingerprint_profile is not None,
            "injection_script_loaded": self._injection_script is not None,
        }
        
        if self._fingerprint_profile:
            status["fingerprint"] = {
                "user_agent": self._fingerprint_profile.user_agent,
                "platform": self._fingerprint_profile.platform,
                "timezone": self._fingerprint_profile.timezone,
                "language": self._fingerprint_profile.language,
                "screen": f"{self._fingerprint_profile.screen_width}x{self._fingerprint_profile.screen_height}",
            }
        
        return status
