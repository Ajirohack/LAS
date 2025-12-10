"""
Example usage of Privacy Cloak Browser.

This demonstrates how to use the privacy features for anonymous browsing.
"""

import asyncio
from privacy_cloak_browser import PrivacyEngine
from privacy_cloak_browser.core.config import PrivacyConfig


async def example_basic_usage():
    """Basic usage with default settings."""
    print("=== Basic Privacy Cloak Browser Example ===\n")
    
    # Create privacy configuration
    config = PrivacyConfig(
        randomize_fingerprint=True,
        use_tor=False,  # Set to True to use Tor
        use_proxy=False,
        enable_human_behavior=True,
        target_platform="generic"
    )
    
    # Create privacy engine
    async with PrivacyEngine(config) as engine:
        # Create privacy-enhanced browser session
        browser_config = await engine.create_browser_session()
        
        print(f"✓ Browser configured with privacy features")
        print(f"  - User Agent: {browser_config['user_agent'][:50]}...")
        print(f"  - Viewport: {browser_config['viewport']}")
        print(f"  - Session Dir: {browser_config['user_data_dir']}")
        
        # Verify privacy
        privacy_check = await engine.verify_privacy()
        print(f"\n✓ Privacy verification: {privacy_check}\n")
        
        # TODO: Use browser_config with browser-use BrowserSession
        # from browser_use import BrowserSession
        # session = BrowserSession(**browser_config)
        # await session.start()
        

async def example_tor_usage():
    """Advanced usage with Tor network."""
    print("=== Privacy Cloak Browser with Tor ===\n")
    
    config = PrivacyConfig(
        use_tor=True,
        block_webrtc=True,
        randomize_canvas=True,
        enable_human_behavior=True,
        target_platform="facebook"
    )
    
    async with PrivacyEngine(config) as engine:
        # Get current IP
        current_ip = await engine.network_anonymizer.get_current_ip()
        print(f"✓ Connected through Tor - IP: {current_ip}")
        
        # Create browser
        browser_config = await engine.create_browser_session()
        
        print(f"✓ Privacy-enhanced browser ready")
        print(f"  - Fingerprint randomized: Yes")
        print(f"  - WebRTC blocked: {config.block_webrtc}")
        print(f"  - Canvas noise: {config.randomize_canvas}")
        

async def example_proxy_usage():
    """Usage with HTTP/SOCKS proxy."""
    print("=== Privacy Cloak Browser with Proxy ===\n")
    
    # Example proxy (replace with your own)
    proxy_url = "http://user:pass@proxy.example.com:8080"
    
    config = PrivacyConfig(
        use_proxy=True,
        proxy_url=proxy_url,
        proxy_rotation_interval=1800,  # Rotate every 30 minutes
        enable_human_behavior=True,
    )
    
    async with PrivacyEngine(config) as engine:
        browser_config = await engine.create_browser_session()
        
        print(f"✓ Browser configured with proxy")
        
        # Get behavior controller for human-like actions
        behavior = engine.get_behavior_controller()
        
        print(f"  - Typing delay: {behavior.get_typing_delay():.3f}s")
        print(f"  - Click delay: {behavior.get_click_delay():.3f}s")
        print(f"  - Scroll speed: {behavior.get_scroll_speed()} px/s")
        

async def example_platform_specific():
    """Platform-specific configuration for Facebook."""
    print("=== Privacy Cloak Browser for Facebook ===\n")
    
    config = PrivacyConfig(
        use_tor=True,  # or use_proxy with residential proxy
        randomize_fingerprint=True,
        randomize_canvas=True,
        randomize_webgl=True,
        randomize_audio=True,
        block_webrtc=True,
        enable_human_behavior=True,
        target_platform="facebook",
        # Longer delays for Facebook
        typing_delay_range=(0.08, 0.2),
        click_delay_range=(0.5, 1.2),
        page_dwell_time_range=(5.0, 15.0),
    )
    
    async with PrivacyEngine(config) as engine:
        browser_config = await engine.create_browser_session()
        
        print(f"✓ Browser optimized for Facebook evasion")
        print(f"  - All fingerprints randomized")
        print(f"  - Human-like behavior enabled")
        print(f"  - Platform-specific delays configured")
        
        # Verify no leaks
        leak_test = await engine.leak_preventer.verify_no_leaks()
        if leak_test['passed']:
            print(f"✓ No leaks detected!")
        else:
            print(f"⚠️ Leaks found: {leak_test['leaks']}")


async def example_identity_rotation():
    """Demonstrate identity rotation."""
    print("=== Identity Rotation Example ===\n")
    
    config = PrivacyConfig(
        randomize_fingerprint=True,
        use_proxy=True,
        proxy_url="http://proxy.example.com:8080",
    )
    
    engine = PrivacyEngine(config)
    await engine.initialize()
    
    # First identity
    config1 = await engine.create_browser_session()
    print(f"Identity 1: {config1['user_agent'][:50]}...")
    
    # Rotate identity
    await engine.rotate_identity()
    
    # New identity
    config2 = await engine.create_browser_session()
    print(f"Identity 2: {config2['user_agent'][:50]}...")
    
    # Verify they're different
    if config1['user_agent'] != config2['user_agent']:
        print("✓ Identity successfully rotated")
    
    await engine.shutdown()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PRIVACY CLOAK BROWSER - Example Usage")
    print("="*60 + "\n")
    
    # Run examples
    asyncio.run(example_basic_usage())
    print("\n" + "-"*60 + "\n")
    
    # Uncomment to test other examples:
    # asyncio.run(example_tor_usage())
    # asyncio.run(example_proxy_usage())
    # asyncio.run(example_platform_specific())
    # asyncio.run(example_identity_rotation())
