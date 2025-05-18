import pytest
import os
from unittest.mock import Mock, patch
from src.clients import LiquipediaClient, LiquipediaDBClient
from src.cache import CacheManager

@pytest.fixture
def cache_manager():
    return CacheManager(redis_url=None, cache_dir="test_cache")

@pytest.fixture
def liquipedia_client():
    with patch.dict(os.environ, {
        'LIQUIPEDIA_USERNAME': 'test_user',
        'LIQUIPEDIA_PASSWORD': 'test_pass'
    }):
        return LiquipediaClient()

@pytest.fixture
def liquipediadb_client():
    with patch.dict(os.environ, {
        'LIQUIPEDIADB_API_KEY': 'test_key'
    }):
        return LiquipediaDBClient()

def test_liquipedia_client_initialization(liquipedia_client):
    assert liquipedia_client.api_username == 'test_user'
    assert liquipedia_client.api_password == 'test_pass'
    assert 'StarCraft-Tournament-Tracker' in liquipedia_client.session.headers['User-Agent']
    assert 'gzip' in liquipedia_client.session.headers['Accept-Encoding']

def test_liquipediadb_client_initialization(liquipediadb_client):
    assert 'Apikey test_key' in liquipediadb_client.session.headers['Authorization']
    assert 'StarCraft-Tournament-Tracker' in liquipediadb_client.session.headers['User-Agent']

@pytest.mark.integration
def test_cache_manager_layers(cache_manager):
    # Test data
    test_key = 'test_tournament'
    test_data = {'name': 'ASL Season 1', 'date': '2023'}
    
    # Test setting and getting from different cache layers
    cache_manager.set(test_key, test_data, 'tournament')
    
    # Should be in memory cache
    assert cache_manager.memory_cache.get(test_key) == test_data
    
    # Should be in file cache
    assert cache_manager.file_cache.get(test_key) == test_data
    
    # Clear memory cache and verify file cache backup
    cache_manager.memory_cache.clear()
    assert cache_manager.get(test_key) == test_data
    
    # Clean up
    cache_manager.clear_all()

@pytest.mark.integration
def test_rate_limiting(liquipedia_client):
    with patch('src.clients.liquipedia_client.time.sleep') as mock_sleep:
        # Make multiple requests to trigger rate limiting
        liquipedia_client.get_page_info('Starcraft:Main_Page')
        liquipedia_client.get_page_info('Starcraft:Tournaments')
        
        # Verify rate limiting was applied
        assert mock_sleep.called

if __name__ == '__main__':
    pytest.main([__file__])
