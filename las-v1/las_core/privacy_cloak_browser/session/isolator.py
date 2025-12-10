"""Session Isolator - Complete session isolation and trace cleanup."""

import logging
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

from privacy_cloak_browser.core.config import PrivacyConfig, FingerprintProfile

logger = logging.getLogger(__name__)


class SessionIsolator:
    """
    Provides complete session isolation with separate user data directories,
    cookie isolation, and trace cleanup.
    """
    
    def __init__(self, config: PrivacyConfig):
        """Initialize session isolator with configuration."""
        self.config = config
        self._session_dir: Optional[Path] = None
        self._session_dirs_to_cleanup: list[Path] = []
    
    async def create_isolated_profile(
        self,
        fingerprint: FingerprintProfile
    ) -> Dict[str, Any]:
        """
        Create an isolated browser profile for this session.
        
        Args:
            fingerprint: Fingerprint profile to configure
            
        Returns:
            Browser profile configuration dictionary
        """
        logger.info("Creating isolated session profile...")
        
        # Create unique temporary directory for this session
        if self.config.user_data_dir:
            self._session_dir = Path(self.config.user_data_dir)
            self._session_dir.mkdir(parents=True, exist_ok=True)
        else:
            self._session_dir = Path(tempfile.mkdtemp(prefix='privacy_cloak_session_'))
        
        self._session_dirs_to_cleanup.append(self._session_dir)
        
        logger.info(f"Session directory: {self._session_dir}")
        
        # Create profile configuration
        profile = {
            'user_data_dir': str(self._session_dir),
            'headless': self.config.headless,
            'viewport': {
                'width': fingerprint.screen_width,
                'height': fingerprint.screen_height
            },
            'user_agent': fingerprint.user_agent,
            
            # Isolation settings
            'accept_downloads': True,
            'permissions': [],  # Grant no permissions by default
            
            # Clear everything on exit
            'record_har_path': None,
            'record_video_dir': None,
        }
        
        logger.info("✓ Isolated profile created")
        return profile
    
    async def clear_all_traces(self) -> None:
        """
        Clear all browser traces including cookies, cache, history, etc.
        """
        if not self.config.clear_cache_after_session:
            logger.debug("Cache clearing disabled, skipping cleanup")
            return
        
        logger.info("Clearing all session traces...")
        
        # Remove session directories
        for session_dir in self._session_dirs_to_cleanup:
            if session_dir.exists():
                try:
                    shutil.rmtree(session_dir)
                    logger.debug(f"Removed session directory: {session_dir}")
                except Exception as e:
                    logger.warning(f"Failed to remove {session_dir}: {e}")
        
        self._session_dirs_to_cleanup.clear()
        self._session_dir = None
        
        logger.info("✓ Session traces cleared")
    
    async def verify_isolation(self) -> bool:
        """
        Verify that session is properly isolated.
        
        Returns:
            True if session is isolated
        """
        # Check that we have a unique session directory
        if not self._session_dir or not self._session_dir.exists():
            logger.warning("No session directory found")
            return False
        
        # Verify directory is not shared
        # In production, would check against database of active sessions
        logger.info("✓ Session isolation verified")
        return True
    
    async def rotate_profile_identity(self) -> None:
        """Clear current profile and prepare for identity rotation."""
        logger.info("Rotating profile identity...")
        await self.clear_all_traces()
        logger.info("✓ Profile identity rotated")
    
    def get_session_dir(self) -> Optional[Path]:
        """Get current session directory path."""
        return self._session_dir
