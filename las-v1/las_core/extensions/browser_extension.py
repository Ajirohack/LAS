from sources.browser import Browser, create_driver
from config.settings import settings
from sdk.decorators import command
from typing import List, Tuple, Optional

class BrowserExtension:
    def __init__(self):
        """
        Initializes the BrowserExtension, creating a persistent browser instance.
        """
        # Default stealth settings
        self.timezone = "Europe/Paris"
        self.resolution = (1920, 1080)
        self.proxy_server = settings.proxy_server
        
        self.browser = self._new_browser()

    def __del__(self):
        """
        Destructor to ensure the browser driver is quit properly.
        """
        try:
            self.browser.driver.quit()
        except:
            pass

    def _new_browser(self) -> Browser:
        """
        Creates a new browser instance based on the application settings.
        """
        driver = create_driver(
            headless=settings.headless_browser, 
            stealth_mode=settings.stealth_mode, 
            lang=settings.languages.split(' ')[0],
            timezone=self.timezone,
            resolution=self.resolution,
            proxy_server=self.proxy_server
        )
        return Browser(driver)

    @command(
        description="Configures the stealth settings for the browser and restarts it with the new settings.",
        arguments={
            "timezone": "Optional. The timezone to use, e.g., 'America/New_York'.",
            "resolution": "Optional. A tuple of (width, height) for the screen resolution, e.g., [1920, 1080].",
            "proxy_server": "Optional. The proxy server to use, e.g., 'http://user:pass@host:port'."
        }
    )
    def configure_stealth(self, timezone: Optional[str] = None, resolution: Optional[Tuple[int, int]] = None, proxy_server: Optional[str] = None) -> str:
        """
        Updates stealth settings and restarts the browser.
        """
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
            
        self.browser = self._new_browser()
        return f"Browser restarted with new stealth settings: timezone={self.timezone}, resolution={self.resolution}, proxy_server={self.proxy_server}"

    @command(
        description="Navigates to a specified URL and returns the text content of the page.",
        arguments={"url": "The URL to browse to."}
    )
    def browse_website(self, url: str) -> str:
        """
        Navigates to a URL and returns the text content.
        """
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
        """
        Sets the browser's geolocation.
        """
        ok = self.browser.set_geolocation(latitude, longitude, accuracy)
        return "Geolocation set successfully." if ok else "Failed to set geolocation."

    @command(
        description="Clicks an element on the page specified by its XPath.",
        arguments={"xpath": "The XPath of the element to click."}
    )
    def click_element(self, xpath: str) -> str:
        """
        Clicks an element specified by XPath.
        """
        ok = self.browser.click_element(xpath)
        return "Element clicked." if ok else "Failed to click element."

    @command(
        description="Fills a form on the current page with the provided data.",
        arguments={"input_list": "A list of strings, where each string is in the format '[input_name](value)'."}
    )
    def fill_form(self, input_list: List[str]) -> str:
        """
        Fills a form and submits it.
        """
        ok = self.browser.fill_form(input_list)
        return "Form filled and submitted successfully." if ok else "Failed to fill or submit form."

    @command(description="Returns a list of all visible input fields on the current page.")
    def get_form_inputs(self) -> List[str]:
        """
        Gets all visible form inputs on the page.
        """
        return self.browser.get_form_inputs()

    @command(description="Returns the current URL of the browser.")
    def get_current_url(self) -> str:
        """
        Gets the current URL.
        """
        return self.browser.get_current_url()

    @command(description="Scrolls to the bottom of the current page.")
    def scroll_bottom(self) -> str:
        """
        Scrolls to the bottom of the page.
        """
        ok = self.browser.scroll_bottom()
        return "Scrolled to bottom." if ok else "Failed to scroll."

    @command(description="Takes a screenshot of the current page and returns the path to the image.")
    def screenshot(self) -> str:
        """
        Takes a screenshot of the page.
        """
        ok = self.browser.screenshot()
        return f"Screenshot saved to {self.browser.get_screenshot()}" if ok else "Failed to take screenshot."
        
    @command(description="Returns the text content of the current page.")
    def get_text(self) -> str:
        """
        Gets the text content of the current page.
        """
        return self.browser.get_text() or "Page was empty or could not be read."

    @command(description="Returns a list of all navigable links on the current page.")
    def get_navigable(self) -> List[str]:
        return self.browser.get_navigable()
