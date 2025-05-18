import time
from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from ratelimit import limits, sleep_and_retry

class BaseClient:
    def __init__(self, base_url: str, user_agent: str):
        self.base_url = base_url
        self.session = self._create_session(user_agent)
    
    def _create_session(self, user_agent: str) -> requests.Session:
        """Create a session with retry logic and proper headers."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            'User-Agent': user_agent,
            'Accept-Encoding': 'gzip',
        })
        
        return session
    
    @sleep_and_retry
    @limits(calls=1, period=2)  # Default rate limit of 1 call per 2 seconds
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """Make a rate-limited request to the API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        response = self.session.request(
            method=method,
            url=url,
            params=params,
            headers=headers,
        )
        
        response.raise_for_status()
        return response
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request to the API."""
        response = self._make_request('GET', endpoint, params=params)
        return response.json()
