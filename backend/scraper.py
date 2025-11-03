# backend/scraper.py

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

# All Jena facilities - using official STW Thüringen website URLs
JENA_MENSAS = {
    'ernst_abbe': {
        'id': 'mensa-ernst-abbe-platz',
        'name': 'Mensa Ernst-Abbe-Platz',
        'address': 'Ernst-Abbe-Platz 8, 07743 Jena',
        'lat': 50.928232,
        'lng': 11.581292,
        'type': 'mensa'
    },
    'carl_zeiss': {
        'id': 'mensa-carl-zeiss-promenade',
        'name': 'Mensa Carl-Zeiss-Promenade',
        'address': 'Carl-Zeiss-Promenade 6, 07745 Jena',
        'lat': 50.917328,
        'lng': 11.568910,
        'type': 'mensa'
    },
    'philosophenweg': {
        'id': 'mensa-philosophenweg',
        'name': 'Mensa Philosophenweg',
        'address': 'Philosophenweg 20, 07743 Jena',
        'lat': 50.933499,
        'lng': 11.584318,
        'type': 'mensa'
    },
    'uni_hauptgebaeude': {
        'id': 'mensa-uni-hauptgebaeude',
        'name': 'Mensa Uni-Hauptgebäude',
        'address': 'Schlossgasse 1, 07743 Jena',
        'lat': 50.928853,
        'lng': 11.589196,
        'type': 'mensa'
    },
    'moritz_von_rohr': {
        'id': 'moritz-von-rohr-strasse',
        'name': 'Mensa Moritz-von-Rohr-Straße',
        'address': 'Moritz-von-Rohr-Straße 5, 07745 Jena',
        'lat': 50.916656,
        'lng': 11.568665,
        'type': 'mensa'
    },
    'zur_rosen': {
        'id': 'cafeteria-zur-rosen',
        'name': 'Cafeteria Zur Rosen',
        'address': 'Johannisstraße 13, 07743 Jena',
        'lat': 50.929340,
        'lng': 11.584751,
        'type': 'cafeteria'
    },
    'carl_zeiss_strasse': {
        'id': 'cafeteria-carl-zeiss-strasse-3',
        'name': 'Cafeteria Carl-Zeiss-Straße',
        'address': 'Carl-Zeiss-Straße 3, 07743 Jena',
        'lat': 50.928907,
        'lng': 11.581192,
        'type': 'cafeteria'
    },
    'bibliothek': {
        'id': 'cafeteria-bibliothek',
        'name': 'Cafeteria Bibliothek',
        'address': 'Bibliotheksplatz 2, 07743 Jena',
        'lat': 50.930275,
        'lng': 11.587494,
        'type': 'cafeteria'
    }
}

def clean_text(text):
    """Remove soft hyphens and clean text while preserving spacing"""
    # Replace soft hyphens with empty string (they're used for hyphenation)
    # Soft hyphens appear at syllable breaks, so removing them joins the word correctly
    text = text.replace('\u00AD', '')
    # Remove other invisible characters
    text = text.replace('\u200B', '')  # Zero-width space
    # Normalize multiple spaces to single space
    text = ' '.join(text.split())
    return text.strip()

def scrape_mensa_menu(mensa_id, date=None):
    """
    Scrape menu from official STW Thüringen website
    """
    if date is None:
        date = datetime.now()
    
    try:
        # URL structure for the official STW website
        url = f'https://www.stw-thueringen.de/mensen/jena/{mensa_id}.html'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.content, 'lxml')
        
        meals = []
        
        # Find all meal names in <div class="mealText">
        meal_divs = soup.find_all('div', class_='mealText')
        
        for meal_div in meal_divs:
            meal_name = clean_text(meal_div.get_text())
            
            if not meal_name or len(meal_name) < 5:
                continue
            
            # Find the parent container to get allergens, price, and dietary info
            parent = meal_div.find_parent()
            if not parent:
                continue
            
            # Walk up to get the full meal container
            meal_container = parent
            for _ in range(3):
                if meal_container.parent:
                    meal_container = meal_container.parent
            
            # Extract dietary symbols from meal-symbols div
            dietary_tags = []
            symbols_div = meal_container.find('div', class_='meal-symbols')
            if symbols_div:
                symbols = symbols_div.get_text().strip().split(',')
                for symbol in symbols:
                    symbol = symbol.strip()
                    if symbol == 'V':
                        dietary_tags.append('vegetarian')
                    elif symbol == 'V*':
                        dietary_tags.append('vegan')
                    elif symbol == 'G':
                        dietary_tags.append('poultry')
                    elif symbol == 'S':
                        dietary_tags.append('pork')
                    elif symbol == 'R':
                        dietary_tags.append('beef')
                    elif symbol == 'F':
                        dietary_tags.append('fish')
                    elif symbol == 'W':
                        dietary_tags.append('game')
                    elif symbol == 'L':
                        dietary_tags.append('lamb')
                    elif symbol == 'Ws':
                        dietary_tags.append('wild_boar')
            
            # Also check image alt tags for dietary info (backup method)
            if not dietary_tags:
                images = meal_container.find_all('img')
                for img in images:
                    alt = img.get('alt', '').lower()
                    if 'vegetarisch' in alt or 'vegetarian' in alt:
                        if 'vegetarian' not in dietary_tags:
                            dietary_tags.append('vegetarian')
                    if 'vegan' in alt:
                        if 'vegan' not in dietary_tags:
                            dietary_tags.append('vegan')
                    if 'geflügel' in alt or 'poultry' in alt:
                        if 'poultry' not in dietary_tags:
                            dietary_tags.append('poultry')
                    if 'schweinefleisch' in alt or 'pork' in alt:
                        if 'pork' not in dietary_tags:
                            dietary_tags.append('pork')
                    if 'rindfleisch' in alt or 'beef' in alt:
                        if 'beef' not in dietary_tags:
                            dietary_tags.append('beef')
                    if 'fisch' in alt or 'fish' in alt:
                        if 'fish' not in dietary_tags:
                            dietary_tags.append('fish')
            
            # Look for allergens in allergen div and extract gluten info
            allergens = ''
            contains_gluten = False
            contains_lactose = False
            allergen_div = meal_container.find('div', class_='allergene')
            if allergen_div:
                allergen_text = allergen_div.get_text()
                allergen_match = re.search(r'Allergene:\s*([A-Za-z,\s]+)', allergen_text)
                if allergen_match:
                    allergens = f"({allergen_match.group(1).strip()})"
                    # Check for gluten-containing grains
                    gluten_markers = ['Wz', 'Ro', 'Gs', 'Hf', 'Di', 'Ka']  # Wheat, Rye, Barley, Oats, Spelt, Kamut
                    # Check for lactose (milk and dairy products)
                    lactose_markers = ['Mi']  # Milk (Milch)
                    allergen_codes = allergen_match.group(1).strip().split(',')
                    contains_gluten = any(marker.strip() in gluten_markers for marker in allergen_codes)
                    contains_lactose = any(marker.strip() in lactose_markers for marker in allergen_codes)
            
            # If no allergen div, check for allergens in zusatzstoffe or parent text
            if not allergens:
                allergen_match = re.search(r'Allergene:\s*([A-Za-z,\s]+)', parent.get_text())
                if allergen_match:
                    allergens = f"({allergen_match.group(1).strip()})"
                    gluten_markers = ['Wz', 'Ro', 'Gs', 'Hf', 'Di', 'Ka']
                    lactose_markers = ['Mi']
                    allergen_codes = allergen_match.group(1).strip().split(',')
                    contains_gluten = any(marker.strip() in gluten_markers for marker in allergen_codes)
                    contains_lactose = any(marker.strip() in lactose_markers for marker in allergen_codes)
            
            # Look for price - search in parent tree for all three price tiers
            # Format: "Studierende* / Bedienstete* / Gäste X,XX / X,XX / X,XX €"
            price_student = 'N/A'
            price_employee = 'N/A'
            price_guest = 'N/A'
            
            # Walk up the tree to find price
            price_parent = parent
            for _ in range(5):
                if price_parent:
                    parent_text = price_parent.get_text()
                    if 'Studierende' in parent_text and '€' in parent_text:
                        # Try to match all three prices in format: X,XX / X,XX / X,XX €
                        price_match = re.search(r'(\d+,\d+)\s*/\s*(\d+,\d+)\s*/\s*(\d+,\d+)\s*€', parent_text)
                        if price_match:
                            price_student = price_match.group(1).replace(',', '.')
                            price_employee = price_match.group(2).replace(',', '.')
                            price_guest = price_match.group(3).replace(',', '.')
                            break
                        # Fallback to old method for student price only
                        price_match = re.search(r'Studierende[^0-9]*(\d+,\d+)', parent_text)
                        if price_match:
                            price_student = price_match.group(1).replace(',', '.')
                            break
                    price_parent = price_parent.parent
            
            # Look for CO2 equivalent information
            # Format: "XXXg CO2-Äquivalent pro Portion" or in image alt text
            co2_equivalent = None
            
            # Check for CO2 in meal container text
            container_text = meal_container.get_text()
            co2_match = re.search(r'(\d+)g?\s*CO2[- ]?(?:Ä|A)quivalent', container_text, re.IGNORECASE)
            if co2_match:
                co2_equivalent = int(co2_match.group(1))
            
            # Also check for CO2 label images with alt text
            if not co2_equivalent:
                co2_images = meal_container.find_all('img', src=re.compile(r'CO2', re.IGNORECASE))
                for img in co2_images:
                    alt_text = img.get('alt', '')
                    co2_match = re.search(r'(\d+)g?\s*CO2', alt_text, re.IGNORECASE)
                    if co2_match:
                        co2_equivalent = int(co2_match.group(1))
                        break
                    # Also check src for pattern like CO2_LABEL_759.png
                    src = img.get('src', '')
                    co2_match = re.search(r'CO2[_-]LABEL[_-](\d+)', src, re.IGNORECASE)
                    if co2_match:
                        co2_equivalent = int(co2_match.group(1))
                        break
            
            meals.append({
                'name': meal_name,
                'allergens': allergens,
                'price_student': price_student,
                'price_employee': price_employee,
                'price_guest': price_guest,
                'co2_equivalent': co2_equivalent,
                'date': date.strftime('%Y-%m-%d'),
                'dietary_tags': dietary_tags,
                'contains_gluten': contains_gluten,
                'contains_lactose': contains_lactose
            })
        
        return meals[:20]  # Limit to 20 meals
    
    except requests.exceptions.RequestException as e:
        print(f"Error scraping {mensa_id}: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error scraping {mensa_id}: {e}")
        return []

def get_all_mensas_menu(date=None):
    """
    Get menus for all Jena mensas and cafeterias
    """
    if date is None:
        date = datetime.now()
    
    all_menus = {}
    
    for key, mensa_info in JENA_MENSAS.items():
        mensa_id = mensa_info['id']
        print(f"Scraping {mensa_info['name']}...")
        menu = scrape_mensa_menu(mensa_id, date)
        
        all_menus[key] = {
            'info': mensa_info,
            'menu': menu
        }
        
        print(f"  Found {len(menu)} meals")
    
    return all_menus

def get_mensa_info():
    """
    Return information about all Jena mensas
    """
    return JENA_MENSAS