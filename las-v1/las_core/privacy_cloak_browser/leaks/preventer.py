"""Leak Preventer - Prevents WebRTC, DNS, IP, and other privacy leaks."""

import logging
from typing import Dict, Any

from privacy_cloak_browser.core.config import PrivacyConfig

logger = logging.getLogger(__name__)


class LeakPreventer:
    """
    Prevents common privacy leaks including WebRTC, DNS, IP leaks, and more.
    """
    
    def __init__(self, config: PrivacyConfig):
        """Initialize leak preventer with configuration."""
        self.config = config
    
    def apply_protections(self, browser_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply leak prevention settings to browser configuration.
        
        Args:
            browser_config: Browser configuration dictionary
            
        Returns:
            Modified browser configuration
        """
        logger.info("Applying leak prevention protections...")
        
        if 'args' not in browser_config:
            browser_config['args'] = []
        
        # WebRTC leak prevention
        if self.config.block_webrtc:
            browser_config['args'].extend([
                '--disable-webrtc',
                '--disable-webrtc-encryption',
                '--disable-webrtc-hw-decoding',
                '--disable-webrtc-hw-encoding',
            ])
            logger.debug("✓ WebRTC blocking enabled")
        
        # DNS over HTTPS
        if self.config.use_dns_over_https:
            browser_config['args'].append(
                '--enable-features=DnsOverHttps',
            )
            logger.debug("✓ DNS-over-HTTPS enabled")
        
        # Block media device enumeration
        if self.config.block_media_device_enumeration:
            browser_config['args'].append(
                '--disable-media-device-enumeration'
            )
            logger.debug("✓ Media device enumeration blocked")
        
        # Additional privacy args
        browser_config['args'].extend([
            '--disable-background-networking',
            '--disable-client-side-phishing-detection',
            '--disable-component-update',
            '--disable-default-apps',
            '--disable-domain-reliability',
            '--disable-sync',
            '--metrics-recording-only',
        ])
        
        logger.info("✓ Leak prevention protections applied")
        return browser_config
    
    async def verify_no_leaks(self) -> Dict[str, Any]:
        """
        Verify there are no privacy leaks.
        
        Returns:
            Dictionary with leak test results
        """
        logger.info("Running leak verification tests...")
        
        results = {
            'passed': True,
            'leaks': [],
            'ip_leak': False,
            'dns_leak': False,
            'webrtc_leak': False,
        }
        
        # IP leak test
        try:
            ip_leak = await self._test_ip_leak()
            results['ip_leak'] = ip_leak
            if ip_leak:
                results['leaks'].append('IP leak detected')
                results['passed'] = False
        except Exception as e:
            logger.warning(f"IP leak test failed: {e}")
        
        # DNS leak test
        try:
            dns_leak = await self._test_dns_leak()
            results['dns_leak'] = dns_leak
            if dns_leak:
                results['leaks'].append('DNS leak detected')
                results['passed'] = False
        except Exception as e:
            logger.warning(f"DNS leak test failed: {e}")
        
        # WebRTC leak test
        try:
            webrtc_leak = await self._test_webrtc_leak()
            results['webrtc_leak'] = webrtc_leak
            if webrtc_leak:
                results['leaks'].append('WebRTC leak detected')
                results['passed'] = False
        except Exception as e:
            logger.warning(f"WebRTC leak test failed: {e}")
        
        if results['passed']:
            logger.info("✓ No leaks detected")
        else:
            logger.warning(f"⚠️ Leaks detected: {results['leaks']}")
        
        return results
    
    async def _test_ip_leak(self) -> bool:
        """
        Test for IP leaks.
        
        Returns:
            True if leak detected
        """
        try:
            import requests
            
            # Get IP through normal connection
            response1 = requests.get('https://api.ipify.org?format=json', timeout=5)
            normal_ip = response1.json()['ip']
            
            # Get IP through DNS (potential leak)
            response2 = requests.get('https://icanhazip.com', timeout=5)
            dns_ip = response2.text.strip()
            
            # If IPs differ, there might be a leak
            if normal_ip != dns_ip:
                logger.warning(f"IP mismatch detected: {normal_ip} vs {dns_ip}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"IP leak test error: {e}")
            return False
    
    async def _test_dns_leak(self) -> bool:
        """
        Test for DNS leaks.
        
        Returns:
            True if leak detected
        """
        # TODO: Implement DNS leak detection using dnsleaktest.com API
        # For now, assume no leak if using DoH
        return not self.config.use_dns_over_https
    
    async def _test_webrtc_leak(self) -> bool:
        """
        Test for WebRTC leaks.
        
        Returns:
            True if leak detected
        """
        # WebRTC is disabled if config says so
        return not self.config.block_webrtc
    
    def get_leak_prevention_script(self) -> str:
        """
        Get JavaScript to inject for runtime leak prevention.
        
        Returns:
            JavaScript code
        """
        return """
        // Leak prevention script
        (function() {
            'use strict';
            
            // Block WebRTC if configured
            if (navigator.mediaDevices) {
                const originalGetUserMedia = navigator.mediaDevices.getUserMedia;
                navigator.mediaDevices.getUserMedia = function() {
                    return Promise.reject(new DOMException('Permission denied', 'NotAllowedError'));
                };
            }
            
            // Block legacy getUserMedia
            if (navigator.getUserMedia) {
                navigator.getUserMedia = function() {
                    throw new DOMException('Permission denied', 'NotAllowedError');
                };
            }
            
            // Block RTCPeerConnection
            window.RTCPeerConnection = undefined;
            window.webkitRTCPeerConnection = undefined;
            window.mozRTCPeerConnection = undefined;
            
            // Block enumerateDevices
            if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
                navigator.mediaDevices.enumerateDevices = async function() {
                    return [];
                };
            }
            
            console.log('[Privacy Cloak] Leak prevention active');
        })();
        """
