import os
from typing import Dict, Any, Optional
from functools import wraps
from ratelimit import limits, sleep_and_retry
from .base_client import BaseClient

class LiquipediaClient(BaseClient):
    def __init__(self):
        user_agent = (
            f"StarCraft-Tournament-Tracker/1.0 "
            f"(contact@email.com; "  # TODO: Replace with actual contact
            f"Project: https://github.com/yourusername/starcraft-tournament-tracker)"
        )
        super().__init__(
            base_url="https://liquipedia.net/api.php",
            user_agent=user_agent
        )
        
        # Set authentication if credentials are provided
        self.api_username = os.getenv('LIQUIPEDIA_USERNAME')
        self.api_password = os.getenv('LIQUIPEDIA_PASSWORD')
        if self.api_username and self.api_password:
            self._authenticate()

    def _authenticate(self):
        """Authenticate with Liquipedia API using credentials."""
        auth_params = {
            'action': 'login',
            'lgname': self.api_username,
            'lgpassword': self.api_password,
            'format': 'json'
        }
        response = self._make_request('POST', '', params=auth_params)
        # Handle token if required by API
        
    @sleep_and_retry
    @limits(calls=1, period=30)  # Specific limit for parse actions
    def get_parsed_page(self, title: str) -> Dict[str, Any]:
        """Get parsed page content with specific rate limit."""
        params = {
            'action': 'parse',
            'page': title,
            'format': 'json'
        }
        return self.get('', params=params)
    
    def get_page_info(self, title: str) -> Dict[str, Any]:
        """Get basic page information using regular rate limit."""
        params = {
            'action': 'query',
            'titles': title,
            'format': 'json'
        }
        return self.get('', params=params)

    def get_category_members(self, category: str) -> Dict[str, Any]:
        """Get members of a category."""
        params = {
            'action': 'query',
            'list': 'categorymembers',
            'cmtitle': category,
            'format': 'json'
        }
        return self.get('', params=params)
