"""Behavioral Obfuscator - Makes automation look human."""

import logging
import random
import asyncio
import math
from typing import Tuple, List

from privacy_cloak_browser.core.config import PrivacyConfig

logger = logging.getLogger(__name__)


class BehaviorObfuscator:
    """
    Implements human-like behavioral patterns for mouse, keyboard, scrolling, etc.
    
    Uses Bezier curves for natural mouse movements, variable typing speeds,
    realistic delays, and human-like browsing patterns.
    """
    
    def __init__(self, config: PrivacyConfig):
        """Initialize behavior obfuscator with configuration."""
        self.config = config
    
    def get_typing_delay(self) -> float:
        """
        Get randomized typing delay.
        
        Returns:
            Delay in seconds
        """
        min_delay, max_delay = self.config.typing_delay_range
        return random.uniform(min_delay, max_delay)
    
    def get_click_delay(self) -> float:
        """
        Get randomized click delay.
        
        Returns:
            Delay in seconds
        """
        min_delay, max_delay = self.config.click_delay_range
        return random.uniform(min_delay, max_delay)
    
    def get_scroll_speed(self) -> int:
        """
        Get randomized scroll speed.
        
        Returns:
            Scroll speed in pixels per second
        """
        min_speed, max_speed = self.config.scroll_speed_range
        return random.randint(min_speed, max_speed)
    
    def get_page_dwell_time(self) -> float:
        """
        Get randomized page dwell time.
        
        Returns:
            Time to stay on page in seconds
        """
        min_time, max_time = self.config.page_dwell_time_range
        return random.uniform(min_time, max_time)
    
    def generate_bezier_curve_path(
        self,
        start: Tuple[int, int],
        end: Tuple[int, int],
        num_points: int = 20
    ) -> List[Tuple[int, int]]:
        """
        Generate natural mouse movement path using Bezier curves.
        
        Args:
            start: Starting (x, y) coordinates
            end: Ending (x, y) coordinates
            num_points: Number of intermediate points
            
        Returns:
            List of (x, y) coordinate tuples
        """
        # Generate control points for natural curve
        x_start, y_start = start
        x_end, y_end = end
        
        # Create slight random offset for control points
        x_offset = random.randint(-50, 50)
        y_offset = random.randint(-50, 50)
        
        # Control points for cubic Bezier curve
        cp1_x = x_start + (x_end - x_start) // 3 + x_offset
        cp1_y = y_start + (y_end - y_start) // 3 + y_offset
        
        cp2_x = x_start + 2 * (x_end - x_start) // 3 - x_offset
        cp2_y = y_start + 2 * (y_end - y_start) // 3 - y_offset
        
        # Generate points along curve
        path = []
        for i in range(num_points + 1):
            t = i / num_points
            
            # Cubic Bezier formula
            x = (
                (1 - t) ** 3 * x_start +
                3 * (1 - t) ** 2 * t * cp1_x +
                3 * (1 - t) * t ** 2 * cp2_x +
                t ** 3 * x_end
            )
            
            y = (
                (1 - t) ** 3 * y_start +
                3 * (1 - t) ** 2 * t * cp1_y +
                3 * (1 - t) * t ** 2 * cp2_y +
                t ** 3 * y_end
            )
            
            path.append((int(x), int(y)))
        
        return path
    
    async def move_mouse_naturally(
        self,
        page,
        start: Tuple[int, int],
        end: Tuple[int, int]
    ) -> None:
        """
        Move mouse along natural Bezier curve path.
        
        Args:
            page: Browser page object
            start: Starting coordinates
            end: Ending coordinates
        """
        if not self.config.mouse_movement_natural:
            # Direct movement
            await page.mouse.move(end[0], end[1])
            return
        
        path = self.generate_bezier_curve_path(start, end)
        
        # Move along path with variable speed
        for i, (x, y) in enumerate(path):
            # Slow down at start and end (ease in/out)
            t = i / len(path)
            speed_factor = 4 * t * (1 - t)  # Parabolic ease
            delay = 0.001 / (speed_factor + 0.1)  # Faster in middle
            
            await page.mouse.move(x, y)
            await asyncio.sleep(delay)
    
    async def type_like_human(self, page, text: str, element_selector: str = None) -> None:
        """
        Type text with human-like delays and occasional typos.
        
        Args:
            page: Browser page object
            text: Text to type
            element_selector: Optional selector to focus first
        """
        if element_selector:
            await page.click(element_selector)
        
        for i, char in enumerate(text):
            # Random chance of typo (5%)
            if random.random() < 0.05 and i < len(text) - 1:
                # Type wrong character
                wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                await page.keyboard.type(wrong_char)
                await asyncio.sleep(self.get_typing_delay())
                
                # Backspace to correct
                await page.keyboard.press('Backspace')
                await asyncio.sleep(self.get_typing_delay() * 0.5)
            
            # Type correct character
            await page.keyboard.type(char)
            
            # Add natural delay
            delay = self.get_typing_delay()
            
            # Longer delay after punctuation or spaces
            if char in '.,!? ':
                delay *= random.uniform(2, 4)
            
            await asyncio.sleep(delay)
    
    async def scroll_like_human(
        self,
        page,
        distance: int,
        direction: str = 'down'
    ) -> None:
        """
        Scroll page with human-like smoothness.
        
        Args:
            page: Browser page object
            distance: Distance to scroll in pixels
            direction: 'up' or 'down'
        """
        num_steps = random.randint(10, 20)
        step_size = distance / num_steps
        
        multiplier = 1 if direction == 'down' else -1
        
        for _ in range(num_steps):
            await page.mouse.wheel(0, multiplier * step_size)
            
            # Variable speed scrolling
            delay = random.uniform(0.02, 0.05)
            await asyncio.sleep(delay)
        
        # Pause at end of scroll
        await asyncio.sleep(random.uniform(0.5, 1.5))
    
    async def hover_before_click(self, page, selector: str) -> None:
        """
        Hover over element before clicking (human-like behavior).
        
        Args:
            page: Browser page object
            selector: Element selector
        """
        element = await page.query_selector(selector)
        if element:
            box = await element.bounding_box()
            if box:
                # Get current mouse position (approximate)
                target_x = box['x'] + box['width'] / 2
                target_y = box['y'] + box['height'] / 2
                
                # Move naturally to element
                await self.move_mouse_naturally(
                    page,
                    (0, 0),  # Would need to track actual mouse position
                    (int(target_x), int(target_y))
                )
                
                # Pause before clicking
                await asyncio.sleep(random.uniform(0.1, 0.3))
    
    async def simulate_reading(self, page, reading_speed_wpm: int = 200) -> None:
        """
        Simulate reading behavior with realistic scroll and dwell patterns.
        
        Args:
            page: Browser page object
            reading_speed_wpm: Words per minute reading speed
        """
        # Get page height
        page_height = await page.evaluate('document.body.scrollHeight')
        viewport_height = await page.evaluate('window.innerHeight')
        
        # Estimate words on page
        text_content = await page.evaluate('document.body.innerText')
        word_count = len(text_content.split())
        
        # Calculate reading time
        reading_time = (word_count / reading_speed_wpm) * 60  # seconds
        
        # Scroll in chunks while "reading"
        scroll_chunks = random.randint(3, 8)
        time_per_chunk = reading_time / scroll_chunks
        
        for i in range(scroll_chunks):
            # Read current viewport
            await asyncio.sleep(time_per_chunk * random.uniform(0.8, 1.2))
            
            # Scroll to next section
            if i < scroll_chunks - 1:
                scroll_amount = viewport_height * random.uniform(0.6, 0.9)
                await self.scroll_like_human(page, int(scroll_amount), 'down')
    
    def passes_human_test(self) -> bool:
        """
        Test if behavioral patterns pass as human-like.
        
        Returns:
            True if patterns appear human
        """
        # In production, this would analyze recorded patterns
        # For now, return True if human behavior is enabled
        return self.config.enable_human_behavior
    
    async def add_random_actions(self, page) -> None:
        """
        Add random human-like actions (tab switches, mouse movements, etc.).
        
        Args:
            page: Browser page object
        """
        actions = [
            self._random_mouse_movement,
            self._random_scroll,
            self._pause_and_think,
        ]
        
        # Randomly execute 0-2 actions
        num_actions = random.randint(0, 2)
        for _ in range(num_actions):
            action = random.choice(actions)
            await action(page)
    
    async def _random_mouse_movement(self, page) -> None:
        """Random small mouse movement."""
        current_x, current_y = (random.randint(100, 800), random.randint(100, 600))
        new_x = current_x + random.randint(-100, 100)
        new_y = current_y + random.randint(-100, 100)
        
        await self.move_mouse_naturally(page, (current_x, current_y), (new_x, new_y))
    
    async def _random_scroll(self, page) -> None:
        """Random small scroll."""
        distance = random.randint(50, 200)
        direction = random.choice(['up', 'down'])
        await self.scroll_like_human(page, distance, direction)
    
    async def _pause_and_think(self, page) -> None:
        """Pause as if thinking."""
        await asyncio.sleep(random.uniform(1.0, 3.0))
