"""
USDA FoodData Central API Integration
Completely free alternative to FatSecret - no authentication required!
API Documentation: https://fdc.nal.usda.gov/api-guide.html
"""

import requests
import time
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class USDANutritionAPI:
    def __init__(self):
        # USDA API is free - get your API key from https://fdc.nal.usda.gov/api-key-signup.html
        self.base_url = 'https://api.nal.usda.gov/fdc/v1'
        self.api_key = os.getenv('USDA_API_KEY', 'DEMO_KEY')
        
    def search_food(self, food_name, max_results=1):
        """
        Search for food in USDA database
        """
        try:
            url = f'{self.base_url}/foods/search'
            params = {
                'query': food_name,
                'pageSize': max_results,
                'api_key': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'foods' in data and len(data['foods']) > 0:
                return data['foods'][0]
            
            return None
        
        except Exception as e:
            return None
    
    def get_food_nutrition(self, food_name):
        """
        Get nutritional information for a food item
        Returns data normalized to per 100g
        """
        try:
            # Clean up the food name aggressively
            # Remove everything in parentheses
            food_name = re.sub(r'\([^)]*\)', '', food_name)
            # Remove all quotes
            food_name = food_name.replace('"', '').replace("'", '')
            # Remove special promotional text patterns
            food_name = re.sub(r'Action[^,]*,', '', food_name, flags=re.IGNORECASE)
            food_name = re.sub(r'Akion[^,]*,', '', food_name, flags=re.IGNORECASE)
            food_name = re.sub(r'Aktion[^,]*,', '', food_name, flags=re.IGNORECASE)
            food_name = re.sub(r'Special[^,]*,', '', food_name, flags=re.IGNORECASE)
            # Remove words like "cafeteria", "mensa", "different", etc
            food_name = re.sub(r'\b(cafeteria|mensa|different|mal\s+anders)\b', ' ', food_name, flags=re.IGNORECASE)
            # Remove "with" and everything after (side dishes)
            food_name = re.split(r',?\s+with\s+', food_name, flags=re.IGNORECASE)[0]
            food_name = re.split(r',?\s+dazu\s+', food_name, flags=re.IGNORECASE)[0]
            # Remove "in" and everything after (preparation method)
            food_name = re.split(r'\s+in\s+', food_name, flags=re.IGNORECASE)[0]
            # Clean up whitespace and commas
            food_name = food_name.replace(',', ' ')
            food_name = ' '.join(food_name.split()).strip()
            
            # If the name is too long or empty after cleaning, extract key ingredients
            if len(food_name) > 50 or len(food_name) < 3:
                # Extract main ingredient words (ignore articles, prepositions)
                words = [w.lower() for w in food_name.split() if len(w) > 2]
                keywords = ['kebab', 'chicken', 'turkey', 'beef', 'pork', 'fish', 'pasta', 
                           'rice', 'salad', 'soup', 'gnocchi', 'pizza', 'burger', 'vegetable',
                           'lentil', 'bean', 'pumpkin', 'potato', 'broccoli', 'schnitzel',
                           'plant-based', 'vegan', 'tofu', 'curry', 'stew', 'wrap']
                main_ingredient = next((w for w in words if w in keywords), None)
                if main_ingredient:
                    food_name = main_ingredient
                else:
                    # Take first 2-3 meaningful words
                    food_name = ' '.join(words[:2]) if words else 'mixed meal'
            
            food_data = self.search_food(food_name)
            
            if not food_data:
                return None
            
            if not food_data:
                return None
            
            # Extract nutrients from foodNutrients array
            nutrients = {}
            for nutrient in food_data.get('foodNutrients', []):
                nutrient_name = nutrient.get('nutrientName', '').lower()
                nutrient_value = nutrient.get('value', 0)
                
                # Look for Energy in KCAL
                if 'energy' in nutrient_name:
                    unit_name = nutrient.get('unitName', '').upper()
                    if unit_name == 'KCAL':
                        nutrients['calories'] = round(nutrient_value)
                # Protein
                elif nutrient_name == 'protein':
                    nutrients['protein'] = round(nutrient_value, 1)
                # Carbohydrates
                elif 'carbohydrate' in nutrient_name and 'by difference' in nutrient_name:
                    nutrients['carbs'] = round(nutrient_value, 1)
                # Fat
                elif 'total lipid (fat)' in nutrient_name or nutrient_name == 'total lipid (fat)':
                    nutrients['fat'] = round(nutrient_value, 1)
            
            # If we found at least calories, return the data
            if 'calories' in nutrients and nutrients['calories'] > 0:
                return {
                    'calories': nutrients.get('calories'),
                    'protein': nutrients.get('protein'),
                    'carbs': nutrients.get('carbs'),
                    'fat': nutrients.get('fat'),
                    'food_name': food_data.get('description', food_name),
                    'serving': 'Per 100g'
                }
            
            return None
        
        except Exception as e:
            return None

def add_nutrition_to_meals(meals):
    """
    Add nutritional information to meals using USDA API
    """
    usda_api = USDANutritionAPI()
    
    for meal in meals:
        try:
            # Use translated name for better matching
            search_name = meal.get('name', '')
            
            # Clean up the name (remove additives, allergens info in parentheses)
            search_name = re.sub(r'\([^)]*\)', '', search_name).strip()
            
            nutrition = usda_api.get_food_nutrition(search_name)
            
            if nutrition:
                meal['nutrition'] = nutrition
            else:
                meal['nutrition'] = None
            
            # Small delay to be respectful to the API
            time.sleep(0.2)
        
        except Exception as e:
            print(f"Error adding nutrition for '{meal.get('name')}': {e}")
            meal['nutrition'] = None
    
    return meals

def calculate_average_calories(meals):
    """
    Calculate average calories for meals that have nutrition data
    """
    calories_list = []
    
    for meal in meals:
        if meal.get('nutrition') and meal['nutrition'].get('calories'):
            calories_list.append(meal['nutrition']['calories'])
    
    if len(calories_list) > 0:
        return round(sum(calories_list) / len(calories_list), 1)
    
    return None
