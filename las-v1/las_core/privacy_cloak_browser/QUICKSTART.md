# Privacy Cloak Browser - Quick Start Guide

## ⚡ Quick Installation & Setup

### 1. Install Dependencies

```bash
cd privacy_cloak_browser
pip install -r requirements.txt
```

### 2. Run Tests

```bash
python test_privacy.py
```

### 3. Run Basic Example

```bash
python example_usage.py
```

---

## 🎯 Common Use Cases

### Use Case 1: Anonymous Browsing with Tor

```python
from privacy_cloak_browser import PrivacyEngine
from privacy_cloak_browser.core.config import PrivacyConfig
import asyncio

async def anonymous_browsing():
    config = PrivacyConfig(
        use_tor=True,
        randomize_fingerprint=True,
        block_webrtc=True,
    )
    
    async with PrivacyEngine(config) as engine:
        # Verify Tor connection
        ip = await engine.network_anonymizer.get_current_ip()
        print(f"Browsing through Tor - IP: {ip}")
        
        # Create privacy-enhanced browser
        browser_config = await engine.create_browser_session()
        
        # Use with your browser automation...

asyncio.run(anonymous_browsing())
```

### Use Case 2: Facebook/Instagram Access

```python
config = PrivacyConfig(
    use_proxy=True,
    proxy_url="http://your-residential-proxy",
    randomize_fingerprint=True,
    target_platform="facebook",
    enable_human_behavior=True,
)

async with PrivacyEngine(config) as engine:
    browser_config = await engine.create_browser_session()
    # Use for Facebook automation...
```

### Use Case 3: Multiple Identities

```python
engine = PrivacyEngine(PrivacyConfig())
await engine.initialize()

# Identity 1
config1 = await engine.create_browser_session()

# Rotate
await engine.rotate_identity()

# Identity 2 (completely different fingerprint)
config2 = await engine.create_browser_session()

await engine.shutdown()
```

---

## 🧪 Testing Your Setup

### Test Fingerprinting

Visit these sites to verify your privacy:

1. **<https://browserleaks.com>** - Check all leaks
2. **<https://deviceinfo.me>** - Device fingerprint
3. **<https://amiunique.org>** - Fingerprint uniqueness
4. **<https://ipleak.net>** - IP/DNS/WebRTC leaks

### Run Automated Tests

```bash
python test_privacy.py
```

Expected output:

```
✅ PASS - Fingerprint Randomization
✅ PASS - Network Anonymization
✅ PASS - Leak Prevention
✅ PASS - Behavioral Patterns
✅ PASS - Session Isolation
✅ PASS - JavaScript Injection

🎉 All tests passed!
```

---

## 🔧 Configuration Reference

### Essential Settings

```python
PrivacyConfig(
    # Fingerprinting
    randomize_fingerprint=True,      # Enable all randomization
    randomize_canvas=True,            # Canvas noise
    randomize_webgl=True,             # WebGL spoofing
    randomize_audio=True,             # Audio fingerprint
    block_webrtc=True,                # Block WebRTC leaks
    
    # Network
    use_tor=False,                    # Use Tor network
    use_vpn=False,                    # Use VPN
    use_proxy=False,                  # Use HTTP/SOCKS proxy
    proxy_url=None,                   # Proxy URL
    
    # Behavior
    enable_human_behavior=True,       # Human-like patterns
    typing_delay_range=(0.05, 0.15),  # Typing delays
    click_delay_range=(0.2, 0.8),     # Click delays
    
    # Platform
    target_platform="generic",        # facebook, instagram, linkedin, etc.
)
```

---

## 🚀 Integration with browser-use

See `integration_examples.py` for detailed examples:

```bash
python integration_examples.py
```

---

## 📝 Best Practices

1. **Use Residential Proxies** for social media (not datacenter)
2. **Match Timezone** to your proxy location
3. **Rotate Identities** every 24-48 hours
4. **Don't Reuse** fingerprints
5. **Monitor** for detection signals
6. **Use Realistic Timing** - don't rush actions

---

## ⚠️ Troubleshooting

### Tor Not Connecting

```bash
# Install Tor
brew install tor  # macOS
sudo apt-get install tor  # Ubuntu

# Start Tor service
brew services start tor  # macOS
sudo service tor start  # Ubuntu
```

### Proxy Not Working

- Verify proxy URL format: `http://user:pass@host:port`
- Test proxy connection manually first
- Check proxy is allowing HTTPS connections

### Fingerprint Not Randomizing

- Ensure `randomize_fingerprint=True`
- Check browser configuration includes custom args
- Verify JavaScript injection scripts are loaded

---

## 📚 Next Steps

1. ✅ Run tests: `python test_privacy.py`
2. ✅ Try examples: `python example_usage.py`
3. ✅ Test integration: `python integration_examples.py`
4. 📖 Read full docs: `README.md`
5. 🔗 Integrate with your project

---

## 💡 Tips

- Start with `target_platform="generic"` for testing
- Use `headless=False` to watch the browser
- Enable `debug_mode=True` for verbose logging
- Test fingerprints on browserleaks.com first

---

**You're ready to go! 🚀**
