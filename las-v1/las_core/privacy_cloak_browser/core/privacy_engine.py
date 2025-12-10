"""Core Privacy Engine that orchestrates all privacy features."""

import logging
import asyncio
from typing import Optional
from pathlib import Path

from privacy_cloak_browser.core.config import PrivacyConfig, FingerprintProfile
from privacy_cloak_browser.fingerprint.randomizer import FingerprintRandomizer
from privacy_cloak_browser.network.anonymizer import NetworkAnonymizer
from privacy_cloak_browser.behavior.obfuscator import BehaviorObfuscator
from privacy_cloak_browser.session.isolator import SessionIsolator
from privacy_cloak_browser.leaks.preventer import LeakPreventer

logger = logging.getLogger(__name__)


class PrivacyEngine:
    """
    Main orchestrator for all privacy features.
    
    Coordinates fingerprint randomization, network anonymization, behavioral obfuscation,
    session isolation, and leak prevention.
    """
    
    def __init__(self, config: Optional[PrivacyConfig] = None):
        """
        Initialize Privacy Engine with configuration.
        
        Args:
            config: Privacy configuration. If None, uses default settings.
        """
        self.config = config or PrivacyConfig()
        self.fingerprint_profile: Optional[FingerprintProfile] = None
        
        # Initialize components
        self.fingerprint_randomizer = FingerprintRandomizer(self.config)
        self.network_anonymizer = NetworkAnonymizer(self.config)
        self.behavior_obfuscator = BehaviorObfuscator(self.config)
        self.session_isolator = SessionIsolator(self.config)
        self.leak_preventer = LeakPreventer(self.config)
        
        self._browser_session = None
        self._is_initialized = False
        
        logger.info(f"PrivacyEngine initialized with config: {self.config}")
    
    async def initialize(self) -> None:
        """Initialize all privacy components."""
        if self._is_initialized:
            logger.warning("PrivacyEngine already initialized")
            return
        
        logger.info("Initializing Privacy Engine components...")
        
        # Generate fresh fingerprint profile
        self.fingerprint_profile = FingerprintProfile.generate_random(
            target_platform=self.config.target_platform
        )
        logger.info(f"Generated fingerprint profile: {self.fingerprint_profile.user_agent}")
        
        # Initialize network anonymization
        if self.config.use_tor:
            await self.network_anonymizer.connect_tor()
        elif self.config.use_vpn:
            await self.network_anonymizer.connect_vpn()
        elif self.config.use_proxy:
            await self.network_anonymizer.set_proxy(self.config.proxy_url)
        
        # Verify no leaks
        if self.config.use_tor or self.config.use_vpn or self.config.use_proxy:
            leak_test = await self.leak_preventer.verify_no_leaks()
            if not leak_test["passed"]:
                raise RuntimeError(f"Leak detected: {leak_test['leaks']}")
            logger.info("✓ No leaks detected")
        
        self._is_initialized = True
        logger.info("✓ Privacy Engine initialized successfully")
    
    async def create_browser_session(self):
        """
        Create a privacy-enhanced browser session.
        
        Returns:
            BrowserSession configured with all privacy features
        """
        if not self._is_initialized:
            await self.initialize()
        
        logger.info("Creating privacy-enhanced browser session...")
        
        # Create isolated session profile
        session_profile = await self.session_isolator.create_isolated_profile(
            self.fingerprint_profile
        )
        
        # Apply fingerprint randomization
        browser_config = self.fingerprint_randomizer.apply_fingerprint(
            session_profile,
            self.fingerprint_profile
        )
        
        # Apply leak prevention
        browser_config = self.leak_preventer.apply_protections(browser_config)
        
        # TODO: Integrate with browser-use BrowserSession
        # For now, return the configuration
        logger.info("✓ Browser session configuration created")
        
        return browser_config
    
    async def shutdown(self) -> None:
        """Gracefully shutdown and clean up all resources."""
        logger.info("Shutting down Privacy Engine...")
        
        # Clear session traces
        if self.config.clear_cache_after_session:
            await self.session_isolator.clear_all_traces()
        
        # Disconnect from anonymization networks
        if self.config.use_tor:
            await self.network_anonymizer.disconnect_tor()
        elif self.config.use_vpn:
            await self.network_anonymizer.disconnect_vpn()
        
        self._is_initialized = False
        logger.info("✓ Privacy Engine shutdown complete")
    
    def get_behavior_controller(self):
        """Get the behavior obfuscator for human-like actions."""
        return self.behavior_obfuscator
    
    async def verify_privacy(self) -> dict:
        """
        Run comprehensive privacy verification tests.
        
        Returns:
            Dictionary with test results
        """
        results = {
            "fingerprint_unique": False,
            "no_ip_leak": False,
            "no_dns_leak": False,
            "no_webrtc_leak": False,
            "behavioral_human_like": False,
            "session_isolated": False,
        }
        
        # Test fingerprint uniqueness
        results["fingerprint_unique"] = self.fingerprint_randomizer.is_unique()
        
        # Test for leaks
        leak_test = await self.leak_preventer.verify_no_leaks()
        results["no_ip_leak"] = leak_test.get("ip_leak", True) is False
        results["no_dns_leak"] = leak_test.get("dns_leak", True) is False
        results["no_webrtc_leak"] = leak_test.get("webrtc_leak", True) is False
        
        # Test behavioral patterns
        results["behavioral_human_like"] = self.behavior_obfuscator.passes_human_test()
        
        # Test session isolation
        results["session_isolated"] = await self.session_isolator.verify_isolation()
        
        all_passed = all(results.values())
        results["all_tests_passed"] = all_passed
        
        logger.info(f"Privacy verification: {results}")
        return results
    
    async def rotate_identity(self) -> None:
        """Rotate to a new fingerprint and session identity."""
        logger.info("Rotating identity...")
        
        # Generate new fingerprint
        self.fingerprint_profile = FingerprintProfile.generate_random(
            target_platform=self.config.target_platform
        )
        
        # Rotate proxy if using one
        if self.config.use_proxy and self.config.proxy_rotation_interval:
            await self.network_anonymizer.rotate_proxy()
        
        # Clear old session data
        await self.session_isolator.clear_all_traces()
        
        logger.info("✓ Identity rotated successfully")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.shutdown()
        return False
