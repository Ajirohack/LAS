"""
Browser-use integration example for Privacy Cloak Browser.

Demonstrates how to use Privacy Cloak Browser with the browser-use framework.
"""

import asyncio
from pathlib import Path

from privacy_cloak_browser import PrivacyEngine
from privacy_cloak_browser.core.config import PrivacyConfig

# NOTE: Uncomment these when browser-use is installed
# from browser_use import Agent, Browser
# from browser_use.browser.profile import BrowserProfile, ProxySettings


async def example_basic_integration():
    """Basic integration with browser-use."""
    print("=== Privacy Cloak + browser-use Integration ===\n")
    
    # Step 1: Configure Privacy Cloak
    privacy_config = PrivacyConfig(
        randomize_fingerprint=True,
        enable_human_behavior=True,
        block_webrtc=True,
        target_platform="generic",
    )
    
    # Step 2: Initialize Privacy Engine
    async with PrivacyEngine(privacy_config) as engine:
        # Get privacy-enhanced browser configuration
        privacy_browser_config = await engine.create_browser_session()
        
        print(f"✓ Privacy configuration generated:")
        print(f"  - User Agent: {privacy_browser_config['user_agent'][:60]}...")
        print(f"  - Viewport: {privacy_browser_config['viewport']}")
        print(f"  - Session Dir: {privacy_browser_config['user_data_dir']}")
        
        # Get JavaScript injection scripts
        anti_detection_script = engine.fingerprint_randomizer.get_injection_script(
            engine.fingerprint_profile
        )
        leak_prevention_script = engine.leak_preventer.get_leak_prevention_script()
        
        print(f"\n✓ Injection scripts prepared:")
        print(f"  - Anti-detection: {len(anti_detection_script)} chars")
        print(f"  - Leak prevention: {len(leak_prevention_script)} chars")
        
        # Step 3: Create browser-use session (when browser-use is installed)
        """
        # Get proxy configuration if using Tor/VPN/Proxy
        proxy_config = engine.network_anonymizer.get_proxy_config()
        
        # Create browser-use profile with privacy settings
        browser_profile = BrowserProfile(
            user_data_dir=privacy_browser_config['user_data_dir'],
            user_agent=privacy_browser_config['user_agent'],
            viewport=privacy_browser_config['viewport'],
            headless=privacy_config.headless,
            proxy=ProxySettings(**proxy_config) if proxy_config else None,
            # Add privacy-specific args
            args=privacy_browser_config.get('args', []),
        )
        
        # Create browser session
        browser = Browser(browser_profile=browser_profile)
        
        # Create agent with privacy-enhanced browser
        agent = Agent(
            task="Your task here",
            browser=browser,
        )
        
        # Inject privacy scripts after page load
        async def inject_privacy_scripts(page):
            await page.evaluate(anti_detection_script)
            await page.evaluate(leak_prevention_script)
        
        # Run agent
        await agent.run()
        """
        
        print("\n✓ Ready for browser-use integration!")
        print("  (Uncomment code when browser-use is installed)")


async def example_tor_with_browser_use():
    """Integration using Tor network."""
    print("\n=== Privacy Cloak + browser-use + Tor ===\n")
    
    privacy_config = PrivacyConfig(
        use_tor=True,  # Enable Tor routing
        randomize_fingerprint=True,
        randomize_canvas=True,
        randomize_webgl=True,
        block_webrtc=True,
        enable_human_behavior=True,
    )
    
    async with PrivacyEngine(privacy_config) as engine:
        # Verify Tor connection
        current_ip = await engine.network_anonymizer.get_current_ip()
        print(f"✓ Tor connection verified")
        print(f"  - Exit IP: {current_ip}")
        
        # Get privacy-enhanced configuration
        browser_config = await engine.create_browser_session()
        
        # Get proxy configuration for Tor
        proxy_config = engine.network_anonymizer.get_proxy_config()
        print(f"\n✓ Proxy configuration:")
        print(f"  - {proxy_config}")
        
        """
        # Use with browser-use
        browser_profile = BrowserProfile(
            user_data_dir=browser_config['user_data_dir'],
            user_agent=browser_config['user_agent'],
            proxy=ProxySettings(**proxy_config),
            headless=False,  # Set to True for headless
        )
        
        browser = Browser(browser_profile=browser_profile)
        
        agent = Agent(
            task="Browse anonymously through Tor",
            browser=browser,
        )
        
        await agent.run()
        """
        
        print("\n✓ Tor + browser-use configuration ready!")


async def example_facebook_automation():
    """Facebook-specific automation with maximum privacy."""
    print("\n=== Facebook Automation with Privacy Cloak ===\n")
    
    privacy_config = PrivacyConfig(
        # Use residential proxy (example)
        use_proxy=True,
        proxy_url="http://user:pass@residential-proxy.example.com:8080",
        
        # Maximum fingerprint randomization
        randomize_fingerprint=True,
        randomize_canvas=True,
        randomize_webgl=True,
        randomize_audio=True,
        randomize_fonts=True,
        block_webrtc=True,
        
        # Human behavior optimized for Facebook
        enable_human_behavior=True,
        mouse_movement_natural=True,
        typing_delay_range=(0.08, 0.20),
        click_delay_range=(0.5, 1.2),
        page_dwell_time_range=(5.0, 15.0),
        
        # Platform-specific
        target_platform="facebook",
    )
    
    async with PrivacyEngine(privacy_config) as engine:
        # Verify privacy
        privacy_check = await engine.verify_privacy()
        print(f"✓ Privacy verification: {privacy_check.get('all_tests_passed', False)}")
        
        browser_config = await engine.create_browser_session()
        behavior = engine.get_behavior_controller()
        
        print(f"\n✓ Facebook-optimized configuration:")
        print(f"  - Typing delay: {behavior.config.typing_delay_range}")
        print(f"  - Click delay: {behavior.config.click_delay_range}")
        print(f"  - Page dwell: {behavior.config.page_dwell_time_range}")
        
        """
        # Use with browser-use
        from privacy_cloak_browser.evasion.platform_specific import PlatformEvasion
        
        browser = Browser(browser_profile=BrowserProfile(**browser_config))
        
        agent = Agent(
            task="Navigate Facebook with realistic patterns",
            browser=browser,
        )
        
        # Apply platform-specific evasion
        page = await browser.get_current_page()
        await PlatformEvasion.facebook_strategy(page)
        
        # Use behavior controller for human-like actions
        await behavior.simulate_reading(page, reading_speed_wpm=200)
        await behavior.scroll_like_human(page, distance=500)
        
        await agent.run()
        """
        
        print("\n✓ Facebook automation ready with maximum privacy!")


async def example_multi_identity_rotation():
    """Demonstrate rotating between multiple identities."""
    print("\n=== Multi-Identity Rotation ===\n")
    
    privacy_config = PrivacyConfig(
        randomize_fingerprint=True,
        isolate_sessions=True,
        clear_cache_after_session=True,
    )
    
    engine = PrivacyEngine(privacy_config)
    await engine.initialize()
    
    identities = []
    
    # Create 3 different identities
    for i in range(3):
        config = await engine.create_browser_session()
        identities.append({
            'id': i + 1,
            'user_agent': config['user_agent'],
            'viewport': config['viewport'],
            'session_dir': config['user_data_dir'],
        })
        
        print(f"Identity {i + 1}:")
        print(f"  UA: {config['user_agent'][:50]}...")
        print(f"  Viewport: {config['viewport']}")
        
        # Rotate to next identity
        if i < 2:
            await engine.rotate_identity()
            print()
    
    print(f"\n✓ Created {len(identities)} unique identities")
    print("  - Each can be used for separate browser sessions")
    print("  - No cross-contamination between identities")
    
    await engine.shutdown()


async def example_behavioral_demonstration():
    """Demonstrate human-like behavioral patterns."""
    print("\n=== Behavioral Patterns Demo ===\n")
    
    privacy_config = PrivacyConfig(enable_human_behavior=True)
    engine = PrivacyEngine(privacy_config)
    
    behavior = engine.get_behavior_controller()
    
    # Demonstrate timing variations
    print("Typing delays (10 samples):")
    for i in range(10):
        delay = behavior.get_typing_delay()
        print(f"  {i+1}. {delay:.3f}s")
    
    print("\nClick delays (5 samples):")
    for i in range(5):
        delay = behavior.get_click_delay()
        print(f"  {i+1}. {delay:.3f}s")
    
    print("\nBezier curve mouse path:")
    path = behavior.generate_bezier_curve_path((0, 0), (500, 300), num_points=10)
    for i, (x, y) in enumerate(path[:5]):
        print(f"  Point {i+1}: ({x}, {y})")
    print(f"  ... ({len(path) - 5} more points)")
    
    print("\n✓ All patterns are randomized for human-like behavior!")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PRIVACY CLOAK BROWSER - browser-use Integration Examples")
    print("="*60 + "\n")
    
    # Run examples
    asyncio.run(example_basic_integration())
    
    # Uncomment to run other examples:
    # asyncio.run(example_tor_with_browser_use())
    # asyncio.run(example_facebook_automation())
    # asyncio.run(example_multi_identity_rotation())
    # asyncio.run(example_behavioral_demonstration())
