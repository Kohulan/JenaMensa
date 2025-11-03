from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit

from scraper import get_all_mensas_menu, get_mensa_info
from translator import batch_translate_meals
from nutrition_usda import add_nutrition_to_meals, calculate_average_calories
from daily_cache import (
    save_daily_cache, 
    load_daily_cache, 
    delete_old_cache,
    is_cache_valid_for_today
)

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

def fetch_and_cache_daily_menu():
    """
    Fetch menu data, translate it, add nutrition info, and cache it.
    This runs at 2 AM daily and on-demand if cache is missing.
    """
    print(f"\n{'='*60}")
    print(f"Starting daily menu fetch at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    try:
        # Delete old cache first
        delete_old_cache()
        
        # Fetch new data for today
        date_obj = datetime.now()
        raw_menus = get_all_mensas_menu(date_obj)
        
        # Translate menus
        translated_menus = batch_translate_meals(raw_menus)
        
        # Add nutrition information to each mensa's menu
        for mensa_key in translated_menus:
            meals = translated_menus[mensa_key]['menu']
            translated_menus[mensa_key]['menu'] = add_nutrition_to_meals(meals)
            
            # Calculate average calories
            avg_calories = calculate_average_calories(meals)
            translated_menus[mensa_key]['average_calories'] = avg_calories
        
        # Save to cache
        success = save_daily_cache(translated_menus)
        
        if success:
            print(f"✓ Daily menu cache updated successfully!")
        else:
            print(f"✗ Failed to save daily cache")
        
        print(f"{'='*60}\n")
        return translated_menus
    
    except Exception as e:
        print(f"✗ Error in fetch_and_cache_daily_menu: {e}")
        print(f"{'='*60}\n")
        return None

def get_cached_data(date=None):
    """
    Get cached data for today. If cache doesn't exist or is outdated, fetch new data.
    
    Args:
        date: Optional date string in 'YYYY-MM-DD' format. If None, uses today.
    
    Returns:
        Dictionary with menu data or None
    """
    # For now, we only support today's date (can extend later for historical data)
    if date is not None:
        requested_date = datetime.strptime(date, '%Y-%m-%d').date()
        today = datetime.now().date()
        
        if requested_date != today:
            # Could implement historical data fetching here if needed
            return None
    
    # Try to load from cache first
    success, cached_data, cache_date = load_daily_cache()
    
    if success and cached_data:
        return cached_data
    
    # Cache doesn't exist or is outdated - fetch new data
    fresh_data = fetch_and_cache_daily_menu()
    
    return fresh_data

# Schedule daily fetch at 2 AM
scheduler.add_job(
    func=fetch_and_cache_daily_menu,
    trigger=CronTrigger(hour=2, minute=0),
    id='daily_menu_fetch',
    name='Fetch and cache daily menu at 2 AM',
    replace_existing=True
)
print(f"✓ Scheduled daily menu fetch at 2:00 AM")

# Check cache on startup and fetch if needed
if not is_cache_valid_for_today():
    print("Fetching fresh menu data...")
    fetch_and_cache_daily_menu()
else:
    print("✓ Using cached menu data")

@app.route('/api/mensas', methods=['GET'])
def get_mensas():
    """
    Get all mensa information without menus
    """
    try:
        mensas_info = get_mensa_info()
        return jsonify({
            'success': True,
            'data': mensas_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/menus', methods=['GET'])
def get_menus():
    """
    Get menus for all mensas
    Query params:
        - date: YYYY-MM-DD format (optional, defaults to today)
    """
    try:
        date = request.args.get('date', None)
        menus = get_cached_data(date)
        
        return jsonify({
            'success': True,
            'data': menus,
            'date': date if date else datetime.now().strftime('%Y-%m-%d')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/mensa/<mensa_key>', methods=['GET'])
def get_mensa_menu(mensa_key):
    """
    Get menu for a specific mensa
    """
    try:
        date = request.args.get('date', None)
        all_menus = get_cached_data(date)
        
        if mensa_key not in all_menus:
            return jsonify({
                'success': False,
                'error': 'Mensa not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': all_menus[mensa_key]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/suggest', methods=['POST'])
def suggest_mensa():
    """
    Suggest best mensa based on dietary requirements
    Request body:
        - dietary_requirements: array of strings (e.g., ['vegetarian', 'vegan', 'meat', 'halal'])
    """
    try:
        data = request.get_json()
        dietary_requirements = data.get('dietary_requirements', [])
        date = data.get('date', None)
        
        all_menus = get_cached_data(date)
        
        # Score each mensa based on dietary matches
        scores = {}
        
        for mensa_key, mensa_data in all_menus.items():
            score = 0
            matching_meals = []
            
            for meal in mensa_data['menu']:
                meal_tags = meal.get('dietary_tags', [])
                contains_gluten = meal.get('contains_gluten', False)
                contains_lactose = meal.get('contains_lactose', False)
                
                # Check dietary requirements against actual tags from HTML
                for requirement in dietary_requirements:
                    req_lower = requirement.lower()
                    
                    if req_lower == 'vegetarian':
                        if 'vegetarian' in meal_tags:
                            score += 1
                            if meal not in matching_meals:
                                matching_meals.append(meal)
                    
                    elif req_lower == 'vegan':
                        if 'vegan' in meal_tags:
                            score += 1.5  # Higher score for vegan
                            if meal not in matching_meals:
                                matching_meals.append(meal)
                    
                    elif req_lower == 'meat':
                        # Check if meal contains any meat
                        meat_tags = ['pork', 'beef', 'poultry', 'fish', 'lamb', 'game', 'wild_boar']
                        if any(tag in meal_tags for tag in meat_tags):
                            score += 1
                            if meal not in matching_meals:
                                matching_meals.append(meal)
                    
                    elif req_lower == 'halal':
                        # Halal excludes pork but allows poultry, beef, lamb
                        # Also includes vegetarian/vegan options
                        halal_compatible = ['poultry', 'beef', 'lamb', 'fish', 'vegetarian', 'vegan']
                        if (any(tag in meal_tags for tag in halal_compatible) and 
                            'pork' not in meal_tags and 
                            'wild_boar' not in meal_tags):
                            score += 1
                            if meal not in matching_meals:
                                matching_meals.append(meal)
                    
                    elif req_lower == 'gluten-free' or req_lower == 'gluten_free':
                        if not contains_gluten:
                            score += 1
                            if meal not in matching_meals:
                                matching_meals.append(meal)
                    
                    elif req_lower == 'lactose-free' or req_lower == 'lactose_free':
                        # Lactose-free meals (no milk/dairy allergen)
                        # Vegan meals are automatically lactose-free
                        if not contains_lactose or 'vegan' in meal_tags:
                            score += 1
                            if meal not in matching_meals:
                                matching_meals.append(meal)
                    
                    # Specific meat types
                    elif req_lower in ['pork', 'beef', 'poultry', 'fish', 'lamb']:
                        if req_lower in meal_tags or (req_lower == 'poultry' and 'poultry' in meal_tags):
                            score += 1
                            if meal not in matching_meals:
                                matching_meals.append(meal)
            
            scores[mensa_key] = {
                'score': score,
                'matching_meals': matching_meals,
                'info': mensa_data['info'],
                'total_meals': len(mensa_data['menu'])
            }
        
        # Sort by score
        sorted_mensas = sorted(scores.items(), key=lambda x: x[1]['score'], reverse=True)
        
        # Return all suggestions with matching meals (not just top 3)
        suggestions = []
        for mensa_key, data in sorted_mensas:
            if data['score'] > 0:
                suggestions.append({
                    'mensa_key': mensa_key,
                    'name': data['info']['name'],
                    'score': data['score'],
                    'matching_meals': data['matching_meals'][:5],  # Top 5 matching meals
                    'address': data['info']['address'],
                    'type': data['info'].get('type', 'mensa'),
                    'coordinates': {
                        'lat': data['info']['lat'],
                        'lng': data['info']['lng']
                    }
                })
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'dietary_requirements': dietary_requirements
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/filter', methods=['POST'])
def filter_meals():
    """
    Filter meals across all mensas based on dietary requirements
    Request body:
        - filters: object with boolean flags (vegetarian, vegan, gluten_free, etc.)
        - date: YYYY-MM-DD format (optional)
    """
    try:
        data = request.get_json()
        filters = data.get('filters', {})
        date = data.get('date', None)
        
        all_menus = get_cached_data(date)
        filtered_results = {}
        
        for mensa_key, mensa_data in all_menus.items():
            matching_meals = []
            
            for meal in mensa_data['menu']:
                meal_tags = meal.get('dietary_tags', [])
                contains_gluten = meal.get('contains_gluten', False)
                
                # Apply filters - all enabled filters must match
                matches = True
                
                if filters.get('vegetarian', False):
                    if 'vegetarian' not in meal_tags:
                        matches = False
                
                if filters.get('vegan', False):
                    if 'vegan' not in meal_tags:
                        matches = False
                
                if filters.get('gluten_free', False):
                    if contains_gluten:
                        matches = False
                
                if filters.get('halal', False):
                    # Exclude pork and wild boar
                    if 'pork' in meal_tags or 'wild_boar' in meal_tags:
                        matches = False
                
                # Meat type filters (if any meat filter is enabled, meal must match one of them)
                meat_filters = []
                if filters.get('pork', False):
                    meat_filters.append('pork')
                if filters.get('beef', False):
                    meat_filters.append('beef')
                if filters.get('poultry', False):
                    meat_filters.append('poultry')
                if filters.get('fish', False):
                    meat_filters.append('fish')
                
                if meat_filters:
                    # If meat filters are specified, meal must contain at least one of them
                    if not any(mf in meal_tags for mf in meat_filters):
                        matches = False
                
                if matches:
                    matching_meals.append(meal)
            
            if matching_meals:
                filtered_results[mensa_key] = {
                    'info': mensa_data['info'],
                    'menu': matching_meals,
                    'total_meals': len(matching_meals)
                }
        
        return jsonify({
            'success': True,
            'data': filtered_results,
            'filters_applied': filters,
            'date': date if date else datetime.now().strftime('%Y-%m-%d')
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/refresh-cache', methods=['POST'])
def refresh_cache():
    """
    Manual endpoint to refresh the daily cache
    Useful for debugging or immediate updates
    """
    try:
        data = fetch_and_cache_daily_menu()
        
        if data:
            return jsonify({
                'success': True,
                'message': 'Cache refreshed successfully',
                'timestamp': datetime.now().isoformat(),
                'mensas_count': len(data)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to refresh cache'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/cache-status', methods=['GET'])
def cache_status():
    """
    Get status of the daily cache
    """
    try:
        success, cached_data, cache_date = load_daily_cache()
        today = datetime.now().strftime('%Y-%m-%d')
        
        return jsonify({
            'success': True,
            'cache_exists': success,
            'cache_date': cache_date,
            'today': today,
            'is_valid': success and cache_date == today,
            'next_scheduled_fetch': '02:00:00 daily'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        'success': True,
        'message': 'Server is running',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 6000))
    app.run(debug=True, host='0.0.0.0', port=port)