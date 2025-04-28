import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Base configuration
BASE_DIR = Path(__file__).parent.parent
CACHE_DIR = BASE_DIR / "cache"

# API Configuration
API_CONFIG = {
    'liquipedia': {
        'username': os.getenv('LIQUIPEDIA_USERNAME'),
        'password': os.getenv('LIQUIPEDIA_PASSWORD'),
        'user_agent': (
            "StarCraft-Tournament-Tracker/1.0 "
            "(contact@email.com; "  # TODO: Replace with actual contact
            "Project: https://github.com/yourusername/starcraft-tournament-tracker)"
        ),
    },
    'liquipediadb': {
        'api_key': os.getenv('LIQUIPEDIADB_API_KEY'),
    }
}

# Cache Configuration
CACHE_CONFIG = {
    'memory': {
        'max_size': 1000,
    },
    'redis': {
        'url': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    },
    'file': {
        'directory': str(CACHE_DIR),
    },
    'ttls': {
        'tournament': 3600,    # 1 hour
        'player': 7200,        # 2 hours
        'static': 86400,       # 24 hours
        'parse': 604800,       # 1 week for parsed pages
    }
}

# Rate Limiting Configuration
RATE_LIMITS = {
    'liquipedia': {
        'general': {'calls': 1, 'period': 2},    # 1 request per 2 seconds
        'parse': {'calls': 1, 'period': 30},     # 1 parse request per 30 seconds
    },
    'liquipediadb': {
        'general': {'calls': 60, 'period': 3600}, # 60 requests per hour
    }
}
