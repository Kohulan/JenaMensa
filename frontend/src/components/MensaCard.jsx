import { useState } from 'react';
import MealItem from './MealItem';
import { toggleFavorite, isFavorite } from '../utils/userPreferences';

function MensaCard({ mensa, onFavoriteChange }) {
  const [expanded, setExpanded] = useState(false);
  const [favorited, setFavorited] = useState(isFavorite(mensa.key));

  const hasMenu = mensa.menu && mensa.menu.length > 0;
  const avgCalories = mensa.average_calories;

  const handleFavoriteClick = () => {
    const newStatus = toggleFavorite(mensa.key);
    setFavorited(newStatus);
    if (onFavoriteChange) {
      onFavoriteChange();
    }
  };

  return (
    <div className={`card group relative ${favorited ? 'ring-2 ring-yellow-400 shadow-xl' : ''}`}>
      {/* Favorite Badge */}
      {favorited && (
        <div className="absolute -top-2 -right-2 bg-yellow-400 text-yellow-900 px-3 py-1 rounded-full text-xs font-bold shadow-lg z-10 flex items-center gap-1">
          ⭐ Favorite
        </div>
      )}
      
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-2xl font-bold text-gray-800 mb-2 group-hover:gradient-text transition-all">
            {mensa.info.name}
          </h3>
          <p className="text-sm text-gray-600 mb-1">
            📍 {mensa.info.address}
          </p>
          <div className="flex items-center gap-2 mt-2">
            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
              mensa.info.type === 'mensa' 
                ? 'bg-red-100 text-red-800 border border-red-200' 
                : 'bg-gray-100 text-gray-700 border border-gray-200'
            }`}>
              {mensa.info.type === 'mensa' ? '🍽️ Dining Hall' : '☕ Cafeteria'}
            </span>
          </div>
        </div>
        
        {/* Favorite Button */}
        <button
          onClick={handleFavoriteClick}
          className={`ml-4 p-3 rounded-full transition-all duration-300 transform hover:scale-110 ${
            favorited 
              ? 'bg-yellow-400 text-yellow-900 shadow-lg hover:bg-yellow-500' 
              : 'glass hover:bg-white/50 text-gray-400'
          }`}
          title={favorited ? 'Remove from favorites' : 'Add to favorites'}
        >
          <svg 
            className="w-6 h-6" 
            fill={favorited ? 'currentColor' : 'none'}
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" 
            />
          </svg>
        </button>
      </div>

      {/* Stats */}
      {hasMenu && (
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="glass rounded-xl p-4 text-center">
            <p className="text-3xl font-bold text-red-600 mb-1">
              {mensa.menu.length}
            </p>
            <p className="text-sm text-gray-600 font-semibold">Dishes Available</p>
          </div>
          {avgCalories && avgCalories > 0 && (
            <div className="glass rounded-xl p-4 text-center">
              <p className="text-3xl font-bold text-orange-600 mb-1">
                {avgCalories}
              </p>
              <p className="text-sm text-gray-600 font-semibold">Avg. Calories</p>
              <p className="text-xs text-gray-500 mt-1">per 100g</p>
            </div>
          )}
        </div>
      )}

      {/* Menu Items */}
      {hasMenu ? (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-bold text-gray-800">
              Today's Menu
            </h4>
            <button
              onClick={() => setExpanded(!expanded)}
              className="text-red-600 hover:text-red-700 font-semibold text-sm transition-colors"
            >
              {expanded ? '▲ Show Less' : '▼ Show All'}
            </button>
          </div>

          <div className="space-y-3">
            {(expanded ? mensa.menu : mensa.menu.slice(0, 3)).map((meal, index) => (
              <MealItem key={index} meal={meal} />
            ))}
          </div>

          {!expanded && mensa.menu.length > 3 && (
            <div className="mt-4 text-center">
              <button
                onClick={() => setExpanded(true)}
                className="btn-secondary text-sm"
              >
                View {mensa.menu.length - 3} More Dishes
              </button>
            </div>
          )}
        </div>
      ) : (
        <div className="glass rounded-xl p-8 text-center">
          <p className="text-gray-600 text-lg">
            😔 No menu available for today
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Please check back later or visit the mensa directly
          </p>
        </div>
      )}

      {/* Coordinates for debugging */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-400">
          Coordinates: {mensa.info.lat}, {mensa.info.lng}
        </p>
      </div>
    </div>
  );
}

export default MensaCard;