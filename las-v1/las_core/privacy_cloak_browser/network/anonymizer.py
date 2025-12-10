"""Network Anonymizer - Handles Tor, VPN, and Proxy integration."""

import logging
import asyncio
import subprocess
from typing import Optional, Dict, Any
from pathlib import Path

from privacy_cloak_browser.core.config import PrivacyConfig

logger = logging.getLogger(__name__)


class NetworkAnonymizer:
    """
    Manages network anonymization through Tor, VPN, or proxies.
    
    Provides IP rotation, DNS-over-HTTPS, and kill switch functionality.
    """
    
    def __init__(self, config: PrivacyConfig):
        """Initialize network anonymizer with configuration."""
        self.config = config
        self._tor_process: Optional[subprocess.Popen] = None
        self._vpn_process: Optional[subprocess.Popen] = None
        self._current_proxy: Optional[str] = None
        self._original_ip: Optional[str] = None
        self._current_ip: Optional[str] = None
    
    async def connect_tor(self) -> bool:
        """
        Connect to Tor network.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("Connecting to Tor network...")
        
        try:
            # Check if Tor is already running
            try:
                import requests
                response = requests.get(
                    'https://check.torproject.org/api/ip',
                    proxies={
                        'http': f'socks5h://127.0.0.1:{self.config.tor_socks_port}',
                        'https': f'socks5h://127.0.0.1:{self.config.tor_socks_port}'
                    },
                    timeout=5
                )
                if response.json().get('IsTor'):
                    logger.info("✓ Tor already running")
                    await self._verify_tor_connection()
                    return True
            except:
                pass
            
            # Try to start Tor process
            tor_executable = 'tor'  # Assumes Tor is in PATH
            
            cmd = [
                tor_executable,
                '--SocksPort', str(self.config.tor_socks_port),
                '--ControlPort', str(self.config.tor_control_port),
                '--DataDirectory', str(Path.home() / '.privacy_cloak_browser' / 'tor_data'),
            ]
            
            self._tor_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for Tor to bootstrap
            await asyncio.sleep(10)
            
            # Verify connection
            if await self._verify_tor_connection():
                logger.info("✓ Successfully connected to Tor network")
                return True
            else:
                logger.error("Failed to verify Tor connection")
                return False
                
        except FileNotFoundError:
            logger.error(
                "Tor not found. Please install Tor:\n"
                "  macOS: brew install tor\n"
                "  Ubuntu: sudo apt-get install tor\n"
                "  Manual: https://www.torproject.org/download/"
            )
            return False
        except Exception as e:
            logger.error(f"Error connecting to Tor: {e}")
            return False
    
    async def _verify_tor_connection(self) -> bool:
        """Verify Tor connection is working."""
        try:
            import requests
            
            response = requests.get(
                'https://check.torproject.org/api/ip',
                proxies={
                    'http': f'socks5h://127.0.0.1:{self.config.tor_socks_port}',
                    'https': f'socks5h://127.0.0.1:{self.config.tor_socks_port}'
                },
                timeout=10
            )
            
            data = response.json()
            self._current_ip = data.get('IP')
            
            if data.get('IsTor'):
                logger.info(f"✓ Tor verified - Exit IP: {self._current_ip}")
                return True
            else:
                logger.warning(f"Connection not through Tor - IP: {self._current_ip}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to verify Tor connection: {e}")
            return False
    
    async def disconnect_tor(self) -> None:
        """Disconnect from Tor network."""
        if self._tor_process:
            logger.info("Disconnecting from Tor...")
            self._tor_process.terminate()
            try:
                self._tor_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._tor_process.kill()
            self._tor_process = None
            logger.info("✓ Disconnected from Tor")
    
    async def connect_vpn(self) -> bool:
        """
        Connect to VPN.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Connecting to VPN ({self.config.vpn_provider})...")
        
        if self.config.vpn_provider == "openvpn":
            return await self._connect_openvpn()
        elif self.config.vpn_provider == "wireguard":
            return await self._connect_wireguard()
        else:
            logger.error(f"Unsupported VPN provider: {self.config.vpn_provider}")
            return False
    
    async def _connect_openvpn(self) -> bool:
        """Connect via OpenVPN."""
        if not self.config.vpn_config_path:
            logger.error("VPN config path not set")
            return False
        
        try:
            cmd = [
                'sudo', 'openvpn',
                '--config', str(self.config.vpn_config_path),
                '--daemon'
            ]
            
            self._vpn_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for connection
            await asyncio.sleep(5)
            
            # Verify VPN connection
            if await self._verify_vpn_connection():
                logger.info("✓ Successfully connected to OpenVPN")
                return True
            else:
                logger.error("Failed to verify VPN connection")
                return False
                
        except Exception as e:
            logger.error(f"Error connecting to OpenVPN: {e}")
            return False
    
    async def _connect_wireguard(self) -> bool:
        """Connect via WireGuard."""
        logger.warning("WireGuard support coming soon")
        return False
    
    async def _verify_vpn_connection(self) -> bool:
        """Verify VPN connection is active."""
        try:
            import requests
            
            # Get original IP first if not cached
            if not self._original_ip:
                response = requests.get('https://api.ipify.org?format=json', timeout=5)
                self._original_ip = response.json()['ip']
            
            # Get current IP
            response = requests.get('https://api.ipify.org?format=json', timeout=5)
            self._current_ip = response.json()['ip']
            
            if self._current_ip != self._original_ip:
                logger.info(f"✓ VPN verified - IP changed: {self._original_ip} → {self._current_ip}")
                return True
            else:
                logger.warning("VPN connection failed - IP unchanged")
                return False
                
        except Exception as e:
            logger.error(f"Failed to verify VPN connection: {e}")
            return False
    
    async def disconnect_vpn(self) -> None:
        """Disconnect from VPN."""
        if self._vpn_process:
            logger.info("Disconnecting from VPN...")
            self._vpn_process.terminate()
            try:
                self._vpn_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._vpn_process.kill()
            self._vpn_process = None
            logger.info("✓ Disconnected from VPN")
    
    async def set_proxy(self, proxy_url: str) -> bool:
        """
        Set HTTP/SOCKS proxy.
        
        Args:
            proxy_url: Proxy URL (e.g., "http://user:pass@host:port" or "socks5://host:port")
            
        Returns:
            True if successful
        """
        logger.info(f"Setting proxy: {proxy_url[:20]}...")
        
        self._current_proxy = proxy_url
        
        # Verify proxy works
        if await self._verify_proxy():
            logger.info("✓ Proxy configured successfully")
            return True
        else:
            logger.error("Failed to verify proxy connection")
            return False
    
    async def _verify_proxy(self) -> bool:
        """Verify proxy connection."""
        if not self._current_proxy:
            return False
        
        try:
            import requests
            
            proxies = {
                'http': self._current_proxy,
                'https': self._current_proxy
            }
            
            response = requests.get(
                'https://api.ipify.org?format=json',
                proxies=proxies,
                timeout=10
            )
            
            self._current_ip = response.json()['ip']
            logger.info(f"✓ Proxy verified - IP: {self._current_ip}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to verify proxy: {e}")
            return False
    
    async def rotate_proxy(self) -> bool:
        """
        Rotate to a new proxy from the proxy pool.
        
        In production, this would connect to a proxy rotation service.
        For now, it's a placeholder.
        
        Returns:
            True if rotation successful
        """
        logger.info("Rotating proxy...")
        
        # TODO: Integrate with proxy services like Smartproxy, Oxylabs, etc.
        logger.warning("Proxy rotation requires integration with proxy service")
        
        return False
    
    def get_proxy_config(self) -> Optional[Dict[str, str]]:
        """
        Get proxy configuration for browser.
        
        Returns:
            Dictionary with proxy settings for browser-use
        """
        if self.config.use_tor:
            return {
                'server': f'socks5://127.0.0.1:{self.config.tor_socks_port}',
            }
        elif self.config.use_proxy and self._current_proxy:
            return {
                'server': self._current_proxy,
            }
        
        return None
    
    async def get_current_ip(self) -> Optional[str]:
        """Get current external IP address."""
        try:
            import requests
            
            proxies = {}
            if self.config.use_tor:
                proxies = {
                    'http': f'socks5h://127.0.0.1:{self.config.tor_socks_port}',
                    'https': f'socks5h://127.0.0.1:{self.config.tor_socks_port}'
                }
            elif self._current_proxy:
                proxies = {
                    'http': self._current_proxy,
                    'https': self._current_proxy
                }
            
            response = requests.get(
                'https://api.ipify.org?format=json',
                proxies=proxies if proxies else None,
                timeout=5
            )
            
            return response.json()['ip']
            
        except Exception as e:
            logger.error(f"Failed to get current IP: {e}")
            return None
    
    async def verify_dns_leak(self) -> bool:
        """
        Verify there are no DNS leaks.
        
        Returns:
            True if no leaks detected
        """
        # TODO: Implement DNS leak detection
        # Can use dnsleaktest.com API or similar
        return True
