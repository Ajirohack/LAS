# Privacy Cloak Browser

A sophisticated, lightweight privacy-focused browser automation system built on top of best-in-class features from browser automation frameworks, VPN/Tor projects, and anti-fingerprinting technologies.

## 🎯 Purpose

Designed to evade aggressive tracking and monitoring on platforms like:

- Facebook & Instagram
- LinkedIn
- Dating websites (Match, Tinder, Bumble, etc.)
- Truth Social
- Any platform with aggressive bot detection

## 🔐 Key Features

### 1. **Fingerprint Randomization**

- Canvas/WebGL/Audio fingerprint noise injection
- User agent rotation
- Screen resolution spoofing
- Timezone/locale matching
- Font fingerprint protection

### 2. **Network Anonymization**

- Tor integration
- VPN support (OpenVPN/WireGuard)
- Proxy rotation (HTTP/SOCKS5)
- DNS-over-HTTPS
- IP leak prevention

### 3. **Behavioral Obfuscation**

- Bezier curve mouse movements
- Human-like typing patterns
- Realistic scrolling
- Variable timing/delays
- Reading simulation

### 4. **Session Isolation**

- Separate user data directories
- Complete cookie isolation
- Cache clearing
- No cross-session tracking

### 5. **Leak Prevention**

- WebRTC leak blocking
- DNS leak protection
- Canvas fingerprinting protection
- Media device enumeration blocking
- Battery status randomization

### 6. **Platform-Specific Evasion**

- Custom strategies per platform
- Realistic activity patterns
- Proper timing/dwell times

## 📦 Installation

```bash
cd /path/to/las_core/privacy_cloak_browser
pip install -r requirements.txt
```

## 🚀 Quick Start

### Basic Usage

```python
import asyncio
from privacy_cloak_browser import PrivacyEngine
from privacy_cloak_browser.core.config import PrivacyConfig

async def main():
    # Configure privacy settings
    config = PrivacyConfig(
        randomize_fingerprint=True,
        enable_human_behavior=True,
        target_platform="facebook"
    )
    
    # Create privacy engine
    async with PrivacyEngine(config) as engine:
        # Create privacy-enhanced browser
        browser_config = await engine.create_browser_session()
        
        # Verify privacy
        privacy_check = await engine.verify_privacy()
        print(f"Privacy status: {privacy_check}")

asyncio.run(main())
```

### With Tor

```python
config = PrivacyConfig(
    use_tor=True,
    block_webrtc=True,
    randomize_canvas=True,
)

async with PrivacyEngine(config) as engine:
    # Automatically routes through Tor
    current_ip = await engine.network_anonymizer.get_current_ip()
    print(f"Tor exit IP: {current_ip}")
```

### With Proxy

```python
config = PrivacyConfig(
    use_proxy=True,
    proxy_url="http://user:pass@proxy.example.com:8080",
    proxy_rotation_interval=1800,  # Rotate every 30 min
)

async with PrivacyEngine(config) as engine:
    browser_config = await engine.create_browser_session()
```

## 🎭 Platform-Specific Usage

### Facebook/Instagram

```python
config = PrivacyConfig(
    use_tor=True,  # or residential proxy
    randomize_fingerprint=True,
    target_platform="facebook",
    # Facebook-specific timing
    typing_delay_range=(0.08, 0.2),
    click_delay_range=(0.5, 1.2),
    page_dwell_time_range=(5.0, 15.0),
)
```

### LinkedIn

```python
config = PrivacyConfig(
    use_proxy=True,
    proxy_url="your_proxy",
target_platform="linkedin",
    # Professional browsing patterns
    page_dwell_time_range=(8.0, 20.0),
)
```

## 🔧 Configuration Options

```python
PrivacyConfig(
    # Fingerprint randomization
    randomize_fingerprint: bool = True
    randomize_canvas: bool = True
    randomize_webgl: bool = True
    randomize_audio: bool = True
    block_webrtc: bool = True
    
    # Network anonymization
    use_tor: bool = False
    use_vpn: bool = False
    use_proxy: bool = False
    proxy_url: str = None
    
    # Behavioral obfuscation
    enable_human_behavior: bool = True
    mouse_movement_natural: bool = True
    typing_delay_range: tuple = (0.05, 0.15)
    click_delay_range: tuple = (0.2, 0.8)
    
    # Platform targeting
    target_platform: str = "generic"  # facebook, instagram, linkedin, dating, truthsocial
)
```

## 📁 Project Structure

```
privacy_cloak_browser/
├── core/
│   ├── privacy_engine.py       # Main orchestrator
│   └── config.py                # Configuration
├── fingerprint/
│   └── randomizer.py            # Fingerprint randomization
├── network/
│   └── anonymizer.py            # Tor/VPN/Proxy
├── behavior/
│   └── obfuscator.py            # Human-like patterns
├── session/
│   └── isolator.py              # Session isolation
├── leaks/
│   └── preventer.py             # Leak prevention
├── evasion/
│   └── platform_specific.py     # Platform strategies
└── scripts/
    └── anti_detection.js        # Client-side injection
```

## ⚠️ Ethical & Legal Considerations

> **IMPORTANT**: This tool is designed for privacy protection and avoiding automated banning on platforms with aggressive tracking. Use responsibly and in compliance with:
>
> - Platform Terms of Service
> - Local privacy laws (GDPR, CCPA, etc.)
> - Computer Fraud and Abuse Act (CFAA)
> - Other applicable regulations

**Recommended Use Cases:**

- Privacy research
- Testing your own applications
- Protecting personal privacy
- Academic research

**NOT Recommended For:**

- Malicious automation
- Violating terms of service
- Circumventing legitimate security

## 🧪 Testing

Run the example usage:

```bash
python example_usage.py
```

Test against fingerprinting sites:

- <https://browserleaks.com>
- <https://deviceinfo.me>
- <https://amiunique.org>
- <https://ipleak.net>

## 🔒 Privacy Verification

```python
# Verify your privacy setup
async with PrivacyEngine(config) as engine:
    results = await engine.verify_privacy()
    
    # Check results
    assert results['fingerprint_unique']
    assert results['no_ip_leak']
    assert results['no_dns_leak']
    assert results['no_webrtc_leak']
    assert results['behavioral_human_like']
```

## 📚 Integration with browser-use

This system is designed to integrate with [browser-use](https://github.com/browser-use/browser-use):

```python
from browser_use import BrowserSession

# Get privacy-enhanced config
browser_config = await engine.create_browser_session()

# Create browser-use session
session = BrowserSession(**browser_config)
await session.start()
```

## 🛡️ Best Practices

1. **Use Residential Proxies** for social media (not datacenter IPs)
2. **Match Timezone** to proxy location
3. **Rotate Identities** every 24-48 hours
4. **Don't Reuse Fingerprints**
5. **Monitor for Detection Signals**
6. **Use Realistic Activity Patterns**
7. **Take Breaks** to simulate real users

## 🌐 Recommended Proxy Providers

For best results with social media:

- [Smartproxy](https://smartproxy.com) - Residential proxies
- [Oxylabs](https://oxylabs.io) - Premium residential
- [Bright Data](https://brightdata.com) - Large proxy pools

## 🔮 Future Enhancements

- [ ] Browser-use integration
- [ ] Proxy pool management
- [ ] Machine learning behavioral patterns
- [ ] Platform detection bypass improvements
- [ ] GUI interface
- [ ] Profile management system

## 📝 License

MIT License - See LICENSE file

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

## ⚡ Performance

- Fingerprint generation: <100ms
- Tor connection: ~10s (first time)
- VPN connection: ~5s
- Session initialization: ~2s

## 📞 Support

For issues or questions:

1. Check existing issues
2. Read documentation
3. Create new issue with details

---

**Built with privacy in mind. Use responsibly.** 🔐
