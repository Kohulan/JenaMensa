/**
 * User Preferences Manager
 * Handles localStorage operations for user-specific preferences
 */

const STORAGE_KEYS = {
  FAVORITES: 'mensa_favorites',
  DIETARY_PREFERENCES: 'mensa_dietary_preferences'
};

/**
 * Get favorite mensas from localStorage
 * @returns {Array} Array of favorite mensa keys
 */
export const getFavorites = () => {
  try {
    const favorites = localStorage.getItem(STORAGE_KEYS.FAVORITES);
    return favorites ? JSON.parse(favorites) : [];
  } catch (error) {
    return [];
  }
};

/**
 * Add a mensa to favorites
 * @param {string} mensaKey - The unique key of the mensa
 */
export const addFavorite = (mensaKey) => {
  try {
    const favorites = getFavorites();
    if (!favorites.includes(mensaKey)) {
      favorites.push(mensaKey);
      localStorage.setItem(STORAGE_KEYS.FAVORITES, JSON.stringify(favorites));
    }
  } catch (error) {
    // Silently fail if localStorage is not available
  }
};

/**
 * Remove a mensa from favorites
 * @param {string} mensaKey - The unique key of the mensa
 */
export const removeFavorite = (mensaKey) => {
  try {
    const favorites = getFavorites();
    const filtered = favorites.filter(key => key !== mensaKey);
    localStorage.setItem(STORAGE_KEYS.FAVORITES, JSON.stringify(filtered));
  } catch (error) {
    // Silently fail if localStorage is not available
  }
};

/**
 * Check if a mensa is favorited
 * @param {string} mensaKey - The unique key of the mensa
 * @returns {boolean}
 */
export const isFavorite = (mensaKey) => {
  const favorites = getFavorites();
  return favorites.includes(mensaKey);
};

/**
 * Toggle favorite status
 * @param {string} mensaKey - The unique key of the mensa
 * @returns {boolean} New favorite status
 */
export const toggleFavorite = (mensaKey) => {
  if (isFavorite(mensaKey)) {
    removeFavorite(mensaKey);
    return false;
  } else {
    addFavorite(mensaKey);
    return true;
  }
};

/**
 * Get dietary preferences from localStorage
 * @returns {Array} Array of dietary requirement strings
 */
export const getDietaryPreferences = () => {
  try {
    const prefs = localStorage.getItem(STORAGE_KEYS.DIETARY_PREFERENCES);
    return prefs ? JSON.parse(prefs) : [];
  } catch (error) {
    return [];
  }
};

/**
 * Save dietary preferences to localStorage
 * @param {Array} preferences - Array of dietary requirement strings
 */
export const saveDietaryPreferences = (preferences) => {
  try {
    localStorage.setItem(STORAGE_KEYS.DIETARY_PREFERENCES, JSON.stringify(preferences));
  } catch (error) {
    // Silently fail if localStorage is not available
  }
};

/**
 * Sort mensas by favorites (favorites first)
 * @param {Array} mensas - Array of mensa objects
 * @param {Array} favorites - Array of favorite mensa keys
 * @returns {Array} Sorted array with favorites first
 */
export const sortByFavorites = (mensas, favorites) => {
  return mensas.sort((a, b) => {
    const aIsFavorite = favorites.includes(a.key);
    const bIsFavorite = favorites.includes(b.key);
    
    if (aIsFavorite && !bIsFavorite) return -1;
    if (!aIsFavorite && bIsFavorite) return 1;
    return 0;
  });
};
