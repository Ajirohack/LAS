"""
Privacy Cloak Browser - A sophisticated privacy-focused browser automation system.

Built on top of browser-use with enhanced fingerprinting resistance, network anonymization,
and behavioral obfuscation to evade aggressive tracking on platforms like Facebook, Instagram,
LinkedIn, dating sites, and Truth Social.
"""

__version__ = "0.1.0"
__author__ = "Privacy Cloak Team"

from privacy_cloak_browser.core.privacy_engine import PrivacyEngine
from privacy_cloak_browser.core.config import PrivacyConfig

__all__ = [
    "PrivacyEngine",
    "PrivacyConfig",
]
