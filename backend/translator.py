# backend/translator.py

from deep_translator import MyMemoryTranslator
from googletrans import Translator as GoogleTranslator
import json
import os
import time
from datetime import datetime, timedelta

# Translation cache file
CACHE_FILE = 'translation_cache.json'

# Rate limiting
last_request_time = 0
MIN_REQUEST_INTERVAL = 0.25  # 250ms between requests

# Initialize backup translator
google_translator = GoogleTranslator()

def load_cache():
    """Load translation cache from file"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cache(cache):
    """Save translation cache to file"""
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        pass

# Load cache at startup
translation_cache = load_cache()

def translate_with_mymemory(text):
    """Translate using MyMemory API"""
    global last_request_time
    
    # Rate limiting - wait if needed
    current_time = time.time()
    time_since_last = current_time - last_request_time
    if time_since_last < MIN_REQUEST_INTERVAL:
        time.sleep(MIN_REQUEST_INTERVAL - time_since_last)
    
    translator = MyMemoryTranslator(source='german', target='english')
    translated = translator.translate(text)
    
    # Update last request time
    last_request_time = time.time()
    
    return translated

def translate_with_google(text):
    """Translate using Google Translate (backup)"""
    try:
        result = google_translator.translate(text, src='de', dest='en')
        return result.text
    except Exception as e:
        raise

def translate_to_english(text):
    """
    Translate German text to English
    - First checks cache
    - Then tries MyMemory (primary)
    - Falls back to Google Translate if MyMemory fails
    """
    global translation_cache
    
    if not text or text.strip() == '':
        return text
    
    # Check cache first
    cache_key = text.lower().strip()
    if cache_key in translation_cache:
        return translation_cache[cache_key]
    
    translated = None
    
    # Try MyMemory first
    try:
        translated = translate_with_mymemory(text)
        
        # Check if we hit rate limit (MyMemory returns specific error messages)
        if translated and 'LIMIT' in translated.upper():
            translated = None
            
    except Exception as e:
        translated = None
    
    # If MyMemory failed, try Google Translate
    if translated is None:
        try:
            translated = translate_with_google(text)
        except Exception as e:
            # Return original text if all translation attempts fail
            return text
    
    # Cache the successful translation
    if translated:
        translation_cache[cache_key] = translated
        
        # Save cache periodically
        if len(translation_cache) % 10 == 0:
            save_cache(translation_cache)
    
    return translated

def translate_meals(meals):
    """
    Translate a list of meal dictionaries from German to English
    """
    translated_meals = []
    
    for meal in meals:
        translated_meal = meal.copy()
        
        # Translate meal name
        translated_meal['name_original'] = meal['name']
        translated_meal['name'] = translate_to_english(meal['name'])
        
        # Keep allergens in original German (they're codes like "Mi, V, Wz")
        
        translated_meals.append(translated_meal)
    
    return translated_meals

def batch_translate_meals(all_menus):
    """
    Translate all meals in the menu dictionary
    """
    translated_menus = {}
    
    for mensa_key, mensa_data in all_menus.items():
        translated_menus[mensa_key] = {
            'info': mensa_data['info'],
            'menu': translate_meals(mensa_data['menu'])
        }
    
    # Save cache after processing all menus
    save_cache(translation_cache)
    
    return translated_menus