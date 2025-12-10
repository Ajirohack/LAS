"""Configuration for Privacy Cloak Browser."""

from dataclasses import dataclass, field
from typing import Optional, Literal
from pathlib import Path


@dataclass
class PrivacyConfig:
    """Configuration for privacy features."""
    
    # Fingerprint randomization
    randomize_fingerprint: bool = True
    randomize_canvas: bool = True
    randomize_webgl: bool = True
    randomize_audio: bool = True
    randomize_fonts: bool = True
    block_webrtc: bool = True
    
    # Network anonymization
    use_tor: bool = False
    use_vpn: bool = False
    use_proxy: bool = False
    proxy_url: Optional[str] = None
    proxy_rotation_interval: int = 3600  # seconds
    tor_control_port: int = 9051
    tor_socks_port: int = 9050
    
    # VPN settings
    vpn_provider: Literal["openvpn", "wireguard", "none"] = "none"
    vpn_config_path: Optional[Path] = None
    
    # Behavioral obfuscation
    enable_human_behavior: bool = True
    mouse_movement_natural: bool = True
    typing_delay_range: tuple[float, float] = (0.05, 0.15)  # seconds
    click_delay_range: tuple[float, float] = (0.2, 0.8)  # seconds
    scroll_speed_range: tuple[int, int] = (200, 600)  # pixels per second
    page_dwell_time_range: tuple[float, float] = (2.0, 8.0)  # seconds
    
    # Session isolation
    isolate_sessions: bool = True
    clear_cache_after_session: bool = True
    rotate_profile_identity: bool = True
    
    # Platform-specific settings
    target_platform: Optional[Literal["facebook", "instagram", "linkedin", "dating", "truthsocial", "generic"]] = "generic"
    
    # Leak prevention
    block_plugin_enumeration: bool = True
    block_media_device_enumeration: bool = True
    spoof_timezone: bool = True
    randomize_battery_status: bool = True
    use_dns_over_https: bool = True
    
    # Advanced settings
    headless: bool = False
    window_size: tuple[int, int] = (1920, 1080)
    user_data_dir: Optional[Path] = None
    debug_mode: bool = False
    
    # Kill switch
    enable_kill_switch: bool = True
    kill_switch_on_vpn_disconnect: bool = True
    
    def __post_init__(self):
        """Validate configuration."""
        if self.use_tor and self.use_vpn:
            raise ValueError("Cannot use both Tor and VPN simultaneously. Choose one.")
        
        if self.use_proxy and not self.proxy_url:
            raise ValueError("proxy_url must be set when use_proxy is True")
        
        if self.vpn_provider != "none" and not self.vpn_config_path:
            raise ValueError("vpn_config_path must be set when using VPN")


@dataclass
class FingerprintProfile:
    """A complete browser fingerprint profile."""
    
    user_agent: str
    screen_width: int
    screen_height: int
    device_pixel_ratio: float
    timezone: str
    language: str
    languages: list[str]
    platform: str
    hardware_concurrency: int
    memory: int  # GB
    webgl_vendor: str
    webgl_renderer: str
    canvas_noise_seed: int
    audio_noise_seed: int
    
    @classmethod
    def generate_random(cls, target_platform: Optional[str] = None) -> "FingerprintProfile":
        """Generate a random but realistic fingerprint profile."""
        import random
        import string
        
        # Common realistic configurations
        resolutions = [(1920, 1080), (1366, 768), (1440, 900), (2560, 1440), (1536, 864)]
        platforms = ["Win32", "MacIntel", "Linux x86_64"]
        timezones = ["America/New_York", "America/Los_Angeles", "Europe/London", "Europe/Paris", "Asia/Tokyo"]
        languages = [
            (["en-US", "en"], "en-US"),
            (["en-GB", "en"], "en-GB"),
            (["fr-FR", "fr"], "fr-FR"),
            (["de-DE", "de"], "de-DE"),
        ]
        
        screen_width, screen_height = random.choice(resolutions)
        platform = random.choice(platforms)
        lang_list, lang = random.choice(languages)
        
        # Generate realistic user agent
        chrome_version = random.randint(120, 131)
        
        if platform == "Win32":
            user_agent = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version}.0.0.0 Safari/537.36"
        elif platform == "MacIntel":
            user_agent = f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version}.0.0.0 Safari/537.36"
        else:
            user_agent = f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version}.0.0.0 Safari/537.36"
        
        return cls(
            user_agent=user_agent,
            screen_width=screen_width,
            screen_height=screen_height,
            device_pixel_ratio=random.choice([1.0, 1.25, 1.5, 2.0]),
            timezone=random.choice(timezones),
            language=lang,
            languages=lang_list,
            platform=platform,
            hardware_concurrency=random.choice([2, 4, 6, 8, 12, 16]),
            memory=random.choice([4, 8, 16, 32]),
            webgl_vendor="Google Inc. (NVIDIA)",
            webgl_renderer=f"ANGLE (NVIDIA, NVIDIA GeForce GTX {random.choice([1050, 1060, 1070, 1080, 1650, 1660])} Ti)",
            canvas_noise_seed=random.randint(1, 1000000),
            audio_noise_seed=random.randint(1, 1000000),
        )
