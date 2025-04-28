import os
from typing import Dict, Any, Optional
from ratelimit import limits, sleep_and_retry
from .base_client import BaseClient

class LiquipediaDBClient(BaseClient):
    def __init__(self):
        user_agent = (
            f"StarCraft-Tournament-Tracker/1.0 "
            f"(contact@email.com; "  # TODO: Replace with actual contact
            f"Project: https://github.com/yourusername/starcraft-tournament-tracker)"
        )
        super().__init__(
            base_url="https://api.liquipedia.net/api/v3",
            user_agent=user_agent
        )
        
        # Set up API key authentication
        self.api_key = os.getenv('LIQUIPEDIADB_API_KEY')
        if not self.api_key:
            raise ValueError("LIQUIPEDIADB_API_KEY environment variable is required")
        
        # Add API key to default headers
        self.session.headers.update({
            'Authorization': f'Apikey {self.api_key}'
        })

    @sleep_and_retry
    @limits(calls=60, period=3600)  # 60 requests per hour
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs):
        """Override base request method with specific rate limit."""
        return super()._make_request(method, endpoint, params, **kwargs)

    def get_player_info(self, player_id: str) -> Dict[str, Any]:
        """Get detailed player information."""
        return self.get(f'/player/{player_id}')

    def get_tournament_info(self, tournament_id: str) -> Dict[str, Any]:
        """Get detailed tournament information."""
        return self.get(f'/tournament/{tournament_id}')

    def search_players(self, query: str) -> Dict[str, Any]:
        """Search for players."""
        params = {'query': query}
        return self.get('/search/players', params=params)

    def search_tournaments(self, query: str) -> Dict[str, Any]:
        """Search for tournaments."""
        params = {'query': query}
        return self.get('/search/tournaments', params=params)
