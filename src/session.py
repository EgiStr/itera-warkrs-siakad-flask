"""
SIAKAD ITERA Session Manager
Handles authentication and session management
"""

import cloudscraper
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class SiakadSession:
    """Manages SIAKAD ITERA session with proper authentication"""
    
    def __init__(self, cookies: Dict[str, str], timeout: int = 20):
        """
        Initialize SIAKAD session
        
        Args:
            cookies: Dictionary containing authentication cookies
            timeout: Request timeout in seconds
        """
        self.cookies = cookies
        self.timeout = timeout
        self.session = self._create_session()
    
    def _create_session(self) -> cloudscraper.CloudScraper:
        """Create and configure cloudscraper session"""
        scraper = cloudscraper.create_scraper()
        scraper.cookies.update(self.cookies)
        return scraper
    
    def get(self, url: str, **kwargs) -> cloudscraper.requests.Response:
        """
        Send GET request
        
        Args:
            url: Target URL
            **kwargs: Additional request parameters
            
        Returns:
            Response object
        """
        kwargs.setdefault('timeout', self.timeout)
        response = self.session.get(url, **kwargs)
        response.raise_for_status()
        return response
    
    def post(self, url: str, data: Optional[Dict] = None, **kwargs) -> cloudscraper.requests.Response:
        """
        Send POST request
        
        Args:
            url: Target URL
            data: POST data
            **kwargs: Additional request parameters
            
        Returns:
            Response object
        """
        kwargs.setdefault('timeout', self.timeout)
        kwargs.setdefault('allow_redirects', True)
        return self.session.post(url, data=data, **kwargs)
    
    def is_authenticated(self, test_url: str) -> bool:
        """
        Test if session is properly authenticated
        
        Args:
            test_url: URL to test authentication against
            
        Returns:
            True if authenticated, False otherwise
        """
        try:
            response = self.get(test_url)
            # Check if we're redirected to login page or get proper content
            return 'login' not in response.url.lower() and response.status_code == 200
        except Exception as e:
            logger.error(f"Authentication test failed: {e}")
            return False
