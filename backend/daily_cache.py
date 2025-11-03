# backend/daily_cache.py

import json
import os
from datetime import datetime
from pathlib import Path

# Cache directory and file
CACHE_DIR = Path(__file__).parent / 'cache'
CACHE_FILE = CACHE_DIR / 'daily_menu_cache.json'

def ensure_cache_dir():
    """Create cache directory if it doesn't exist"""
    CACHE_DIR.mkdir(exist_ok=True)

def get_cache_filepath():
    """Get the cache file path"""
    ensure_cache_dir()
    return CACHE_FILE

def save_daily_cache(menu_data):
    """
    Save the daily menu cache (translated and with nutrition info)
    
    Args:
        menu_data: Dictionary containing all mensa menus with translations
    """
    ensure_cache_dir()
    
    cache_data = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'timestamp': datetime.now().isoformat(),
        'data': menu_data
    }
    
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        return False

def load_daily_cache():
    """
    Load the daily menu cache
    
    Returns:
        tuple: (success: bool, data: dict or None, cache_date: str or None)
    """
    if not CACHE_FILE.exists():
        return False, None, None
    
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        cache_date = cache_data.get('date')
        today = datetime.now().strftime('%Y-%m-%d')
        
        if cache_date == today:
            return True, cache_data.get('data'), cache_date
        else:
            return False, None, cache_date
    
    except Exception as e:
        return False, None, None

def delete_old_cache():
    """Delete the old cache file"""
    if CACHE_FILE.exists():
        try:
            os.remove(CACHE_FILE)
            return True
        except Exception as e:
            return False
    return True

def is_cache_valid_for_today():
    """
    Check if cache exists and is valid for today
    
    Returns:
        bool: True if cache is valid for today, False otherwise
    """
    success, _, _ = load_daily_cache()
    return success
