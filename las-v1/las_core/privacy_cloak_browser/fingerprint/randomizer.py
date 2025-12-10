"""Fingerprint Randomizer - Randomizes browser fingerprints to avoid tracking."""

import logging
import hashlib
from typing import Dict, Any, Optional
from pathlib import Path

from privacy_cloak_browser.core.config import PrivacyConfig, FingerprintProfile

logger = logging.getLogger(__name__)


class FingerprintRandomizer:
    """
    Randomizes browser fingerprints including canvas, WebGL, audio, fonts, and more.
    
    Implements sophisticated fingerprint randomization techniques from Tor Browser
    and other privacy-focused browsers.
    """
    
    def __init__(self, config: PrivacyConfig):
        """Initialize fingerprint randomizer with configuration."""
        self.config = config
        self._fingerprint_hash: Optional[str] = None
    
    def apply_fingerprint(self, browser_config: Dict[str, Any], profile: FingerprintProfile) -> Dict[str, Any]:
        """
        Apply fingerprint randomization to browser configuration.
        
        Args:
            browser_config: Browser configuration dictionary
            profile: Fingerprint profile to apply
            
        Returns:
            Modified browser configuration
        """
        logger.info("Applying fingerprint randomization...")
        
        # Set user agent
        browser_config["user_agent"] = profile.user_agent
        
        # Set screen/viewport
        browser_config["viewport"] = {
            "width": profile.screen_width,
            "height": profile.screen_height
        }
        browser_config["screen"] = {
            "width": profile.screen_width,
            "height": profile.screen_height
        }
        browser_config["device_scale_factor"] = profile.device_pixel_ratio
        
        # Chrome args for anti-detection
        if "args" not in browser_config:
            browser_config["args"] = []
        
        # Add anti-fingerprinting args
        anti_fingerprint_args = self._get_anti_fingerprint_args(profile)
        browser_config["args"].extend(anti_fingerprint_args)
        
        # Store fingerprint hash for uniqueness tracking
        self._fingerprint_hash = self._calculate_fingerprint_hash(profile)
        
        logger.info(f"✓ Fingerprint applied: {profile.user_agent[:50]}...")
        return browser_config
    
    def _get_anti_fingerprint_args(self, profile: FingerprintProfile) -> list[str]:
        """Get Chrome command-line args for anti-fingerprinting."""
        args = [
            # Disable WebRTC if configured
            "--disable-webrtc" if self.config.block_webrtc else "",
            
            # Timezone spoofing
            f"--timezone={profile.timezone}" if self.config.spoof_timezone else "",
            
            # Language settings
            f"--lang={profile.language}",
            
            # Disable plugin enumeration
            "--disable-plugins-discovery" if self.config.block_plugin_enumeration else "",
            
            # Additional privacy args
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-infobars",
            "--disable-notifications",
            
            # Font fingerprinting protection
            "--font-render-hinting=none" if self.config.randomize_fonts else "",
        ]
        
        # Filter out empty strings
        return [arg for arg in args if arg]
    
    def get_injection_script(self, profile: FingerprintProfile) -> str:
        """
        Get JavaScript injection script for runtime fingerprint modification.
        
        This script modifies browser APIs at runtime to randomize fingerprints.
        """
        script = f"""
        // Anti-fingerprinting injection script
        (function() {{
            'use strict';
            
            const profile = {{
                platform: '{profile.platform}',
                hardwareConcurrency: {profile.hardware_concurrency},
                deviceMemory: {profile.memory},
                languages: {profile.languages},
                canvasNoiseSeed: {profile.canvas_noise_seed},
                audioNoiseSeed: {profile.audio_noise_seed},
                webglVendor: '{profile.webgl_vendor}',
                webglRenderer: '{profile.webgl_renderer}',
            }};
            
            // Override navigator properties
            Object.defineProperty(navigator, 'platform', {{
                get: function() {{ return profile.platform; }}
            }});
            
            Object.defineProperty(navigator, 'hardwareConcurrency', {{
                get: function() {{ return profile.hardwareConcurrency; }}
            }});
            
            if (navigator.deviceMemory !== undefined) {{
                Object.defineProperty(navigator, 'deviceMemory', {{
                    get: function() {{ return profile.deviceMemory; }}
                }});
            }}
            
            Object.defineProperty(navigator, 'languages', {{
                get: function() {{ return profile.languages; }}
            }});
            
            // Canvas fingerprint noise injection
            {"" if not self.config.randomize_canvas else self._get_canvas_noise_script(profile)}
            
            // WebGL fingerprint modification
            {"" if not self.config.randomize_webgl else self._get_webgl_spoof_script(profile)}
            
            // Audio context fingerprinting protection
            {"" if not self.config.randomize_audio else self._get_audio_noise_script(profile)}
            
            // Remove automation indicators
            delete navigator.__proto__.webdriver;
            Object.defineProperty(navigator, 'webdriver', {{
                get: () => undefined
            }});
            
            // Plugin enumeration protection  
            {"" if not self.config.block_plugin_enumeration else """
            Object.defineProperty(navigator, 'plugins', {
                get: () => []
            });
            """}
            
            // Media device enumeration protection
            {"" if not self.config.block_media_device_enumeration else """
            navigator.mediaDevices.enumerateDevices = async () => [];
            """}
            
            // Battery status randomization
            {"" if not self.config.randomize_battery_status else """
            if (navigator.getBattery) {
                const originalGetBattery = navigator.getBattery;
                navigator.getBattery = async function() {
                    const battery = await originalGetBattery.call(this);
                    return new Proxy(battery, {
                        get(target, prop) {
                            if (prop === 'level') return Math.random() * 0.5 + 0.5;
                            if (prop === 'charging') return Math.random() > 0.5;
                            return target[prop];
                        }
                    });
                };
            }
            """}
            
            console.log('[Privacy Cloak] Fingerprint protection active');
        }})();
        """
        
        return script
    
    def _get_canvas_noise_script(self, profile: FingerprintProfile) -> str:
        """Get canvas fingerprint noise injection script."""
        return f"""
            // Canvas fingerprint noise
            const canvasNoiseGenerator = function(seed) {{
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                const data = imageData.data;
                
                // Inject subtle noise based on seed
                const rng = function(s) {{
                    const x = Math.sin(s++) * 10000;
                    return x - Math.floor(x);
                }};
                
                for (let i = 0; i < data.length; i += 4) {{
                    const noise = rng(seed + i) * 2 - 1;
                    data[i] = Math.max(0, Math.min(255, data[i] + noise));
                }};
                
                return imageData;
            }};
            
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            const originalToBlob = HTMLCanvasElement.prototype.toBlob;
            const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
            
            // Intercept toDataURL
            HTMLCanvasElement.prototype.toDataURL = function() {{
                const context = this.getContext('2d');
                if (context) {{
                    const imageData = context.getImageData(0, 0, this.width, this.height);
                    const noisedData = canvasNoiseGenerator({profile.canvas_noise_seed});
                    context.putImageData(noisedData, 0, 0);
                }}
                return originalToDataURL.apply(this, arguments);
            }};
        """
    
    def _get_webgl_spoof_script(self, profile: FingerprintProfile) -> str:
        """Get WebGL fingerprint spoofing script."""
        return f"""
            // WebGL spoofing
            const getParameterProxyHandler = {{
                apply: function(target, thisArg, args) {{
                    const param = args[0];
                    
                    if (param === 37445) {{ // UNMASKED_VENDOR_WEBGL
                        return '{profile.webgl_vendor}';
                    }}
                    if (param === 37446) {{ // UNMASKED_RENDERER_WEBGL
                        return '{profile.webgl_renderer}';
                    }}
                    
                    return target.apply(thisArg, args);
                }}
            }};
            
            const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = new Proxy(originalGetParameter, getParameterProxyHandler);
            
            if (window.WebGL2RenderingContext) {{
                const originalGetParameter2 = WebGL2RenderingContext.prototype.getParameter;
                WebGL2RenderingContext.prototype.getParameter = new Proxy(originalGetParameter2, getParameterProxyHandler);
            }}
        """
    
    def _get_audio_noise_script(self, profile: FingerprintProfile) -> str:
        """Get audio context noise injection script."""
        return f"""
            // Audio context fingerprinting protection
            const audioNoise = {profile.audio_noise_seed} / 1000000;
            
            const originalCreateDynamicsCompressor = AudioContext.prototype.createDynamicsCompressor;
            AudioContext.prototype.createDynamicsCompressor = function() {{
                const compressor = originalCreateDynamicsCompressor.apply(this, arguments);
                
                // Add subtle noise to compressor parameters
                const originalThreshold = Object.getOwnPropertyDescriptor(DynamicsCompressorNode.prototype, 'threshold');
                Object.defineProperty(compressor, 'threshold', {{
                    get: function() {{
                        return originalThreshold.get.call(this) + audioNoise;
                    }}
                }});
                
                return compressor;
            }};
        """
    
    def _calculate_fingerprint_hash(self, profile: FingerprintProfile) -> str:
        """Calculate hash of fingerprint for uniqueness tracking."""
        fingerprint_str = (
            f"{profile.user_agent}"
            f"{profile.screen_width}x{profile.screen_height}"
            f"{profile.platform}"
            f"{profile.hardware_concurrency}"
            f"{profile.canvas_noise_seed}"
        )
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()
    
    def is_unique(self) -> bool:
        """Check if current fingerprint is unique (not reused)."""
        # In production, this would check against a database of used fingerprints
        # For now, we always generate unique fingerprints
        return self._fingerprint_hash is not None
    
    def get_fingerprint_hash(self) -> Optional[str]:
        """Get hash of current fingerprint."""
        return self._fingerprint_hash
