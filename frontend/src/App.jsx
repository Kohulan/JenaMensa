import { useState, useEffect } from 'react';
import axios from 'axios';
import MensaCard from './components/MensaCard';
import DietaryFilter from './components/DietaryFilter';
import Map from './components/Map';
import LoadingScreen from './components/LoadingScreen';
import { 
  getFavorites, 
  sortByFavorites, 
  getDietaryPreferences, 
  saveDietaryPreferences 
} from './utils/userPreferences';

function App() {
  const [mensas, setMensas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [error, setError] = useState(null);
  const [dietaryRequirements, setDietaryRequirements] = useState(getDietaryPreferences());
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [favorites, setFavorites] = useState(getFavorites());

  useEffect(() => {
    fetchMensaData();
  }, []);

  // Save dietary preferences whenever they change
  useEffect(() => {
    saveDietaryPreferences(dietaryRequirements);
  }, [dietaryRequirements]);

  // Sort mensas whenever favorites change
  useEffect(() => {
    if (mensas.length > 0) {
      const sortedMensas = [...mensas];
      sortByFavorites(sortedMensas, favorites);
      setMensas(sortedMensas);
    }
  }, [favorites]);

  const fetchMensaData = async () => {
    try {
      setLoading(true);
      setLoadingProgress(0);
      setLoadingMessage('Connecting to server');
      
      // Progress simulation during load
      let progressInterval;
      let currentProgress = 0;
      
      const startProgressSimulation = () => {
        progressInterval = setInterval(() => {
          currentProgress += 1;
          if (currentProgress <= 80) { // Cap at 80% until real data arrives
            setLoadingProgress(currentProgress);
            
            // Update messages based on progress
            if (currentProgress < 15) {
              setLoadingMessage('Connecting to server');
            } else if (currentProgress < 30) {
              setLoadingMessage('Requesting menu data');
            } else if (currentProgress < 50) {
              setLoadingMessage('Fetching from all mensas');
            } else if (currentProgress < 65) {
              setLoadingMessage('Loading meal information');
            } else {
              setLoadingMessage('Getting nutrition data');
            }
          }
        }, 100); // Update every 100ms for smooth progress
      };
      
      startProgressSimulation();
      
      const response = await axios.get('/api/menus');
      
      // Clear the simulation and jump to processing stage
      clearInterval(progressInterval);
      setLoadingProgress(85);
      setLoadingMessage('Processing menu information');
      
      if (response.data.success) {
        await new Promise(resolve => setTimeout(resolve, 200));
        setLoadingProgress(92);
        setLoadingMessage('Organizing data');
        
        const mensaArray = Object.entries(response.data.data).map(([key, value]) => ({
          key,
          ...value
        }));
        
        // Sort by favorites
        const sortedMensas = sortByFavorites(mensaArray, getFavorites());
        
        await new Promise(resolve => setTimeout(resolve, 150));
        setLoadingProgress(98);
        setLoadingMessage('Finalizing');
        
        setMensas(sortedMensas);
        
        await new Promise(resolve => setTimeout(resolve, 100));
        setLoadingProgress(100);
        setLoadingMessage('Complete!');
        
        // Small delay to show 100% before hiding
        setTimeout(() => {
          setLoading(false);
        }, 300);
      }
    } catch (err) {
      setError('Failed to load mensa data. Please try again.');
      setLoading(false);
    }
  };

  const handleFavoriteChange = () => {
    // Update favorites state to trigger re-sort
    setFavorites(getFavorites());
  };

  const handleGetSuggestions = async () => {
    if (dietaryRequirements.length === 0) {
      alert('Please select at least one dietary requirement');
      return;
    }

    try {
      const response = await axios.post('/api/suggest', {
        dietary_requirements: dietaryRequirements
      });

      if (response.data.success) {
        setSuggestions(response.data.suggestions);
        setShowSuggestions(true);
      }
    } catch (err) {
      alert('Failed to get suggestions. Please try again.');
    }
  };

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-red-100/40 via-rose-100/30 to-red-50/20 animate-float"></div>
        
        <div className="relative container mx-auto px-4 py-16">
          <div className="text-center mb-12 animate-fade-in">
            <h1 className="text-6xl font-bold mb-4 gradient-text">
              Jena Mensa Finder
            </h1>
            <p className="text-xl text-gray-700 mb-8">
              Discover delicious meals at Jena's university dining halls
            </p>
            
            {/* Date Display */}
            <div className="glass-strong inline-block px-6 py-3 rounded-full mb-8">
              <p className="text-lg font-semibold text-gray-800">
                📅 Today's Menu: {new Date().toLocaleDateString('en-US', { 
                  weekday: 'long', 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}
              </p>
            </div>
          </div>

          {/* Dietary Filter */}
          <div className="max-w-[1400px] mx-auto mb-12 animate-slide-up">
            <DietaryFilter 
              dietaryRequirements={dietaryRequirements}
              setDietaryRequirements={setDietaryRequirements}
              onGetSuggestions={handleGetSuggestions}
            />
          </div>

          {/* Suggestions */}
          {showSuggestions && suggestions.length > 0 && (
            <div className="max-w-[1800px] mx-auto mb-12 animate-fade-in">
              <div className="glass-strong rounded-2xl p-8">
                <h2 className="text-3xl font-bold mb-6 gradient-text">
                  🎯 Recommended For You
                </h2>
                
                {/* Main Dining Halls with matches */}
                {suggestions.filter(s => s.type === 'mensa').length > 0 && (
                  <div className="mb-8">
                    <h3 className="text-xl font-bold mb-4 text-gray-800">
                      🍽️ Main Dining Halls
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                      {suggestions.filter(s => s.type === 'mensa').map((suggestion, index) => (
                        <div 
                          key={index}
                          className="card bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-300"
                        >
                          <h3 className="text-xl font-bold mb-2 text-green-800">
                            {suggestion.name}
                          </h3>
                          <p className="text-sm text-gray-600 mb-4">
                            📍 {suggestion.address}
                          </p>
                          <div className="bg-green-100 rounded-lg p-3 mb-3">
                            <p className="text-sm font-semibold text-green-800">
                              Match Score: {suggestion.score} ⭐
                            </p>
                          </div>
                          {suggestion.matching_meals.length > 0 && (
                            <div>
                              <p className="text-sm font-semibold mb-2 text-gray-700">
                                Recommended Dishes:
                              </p>
                              <ul className="text-sm space-y-1">
                                {suggestion.matching_meals.slice(0, 3).map((meal, mIndex) => (
                                  <li key={mIndex} className="text-gray-600">
                                    • {meal.name}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Cafeterias with matches */}
                {suggestions.filter(s => s.type === 'cafeteria').length > 0 && (
                  <div>
                    <h3 className="text-xl font-bold mb-4 text-gray-800">
                      ☕ Cafeterias
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {suggestions.filter(s => s.type === 'cafeteria').map((suggestion, index) => (
                        <div 
                          key={index}
                          className="card bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-300"
                        >
                          <h3 className="text-xl font-bold mb-2 text-green-800">
                            {suggestion.name}
                          </h3>
                          <p className="text-sm text-gray-600 mb-4">
                            📍 {suggestion.address}
                          </p>
                          <div className="bg-green-100 rounded-lg p-3 mb-3">
                            <p className="text-sm font-semibold text-green-800">
                              Match Score: {suggestion.score} ⭐
                            </p>
                          </div>
                          {suggestion.matching_meals.length > 0 && (
                            <div>
                              <p className="text-sm font-semibold mb-2 text-gray-700">
                                Recommended Dishes:
                              </p>
                              <ul className="text-sm space-y-1">
                                {suggestion.matching_meals.slice(0, 3).map((meal, mIndex) => (
                                  <li key={mIndex} className="text-gray-600">
                                    • {meal.name}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Mensa Cards */}
          <div className="max-w-[1800px] mx-auto">
            {loading ? (
              <LoadingScreen loadingProgress={loadingProgress} loadingMessage={loadingMessage} />
            ) : error ? (
              <div className="glass-strong rounded-2xl p-8 text-center">
                <p className="text-red-600 text-xl font-semibold">{error}</p>
                <button 
                  onClick={fetchMensaData}
                  className="btn-primary mt-4"
                >
                  Try Again
                </button>
              </div>
            ) : (
              <div className="space-y-8">
                <h2 className="text-4xl font-bold text-center gradient-text mb-8">
                  All Mensa & Cafeteria Menus
                </h2>
                
                {/* Favorites Section */}
                {favorites.length > 0 && (
                  <div className="mb-12">
                    <div className="flex items-center gap-3 mb-6">
                      <h3 className="text-3xl font-bold text-gray-800">
                        ⭐ Your Favorites
                      </h3>
                      <span className="bg-yellow-400 text-yellow-900 px-3 py-1 rounded-full text-sm font-bold">
                        {favorites.length}
                      </span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                      {mensas.filter(m => favorites.includes(m.key)).map((mensa, index) => (
                        <div key={index} className="animate-slide-up" style={{animationDelay: `${index * 0.1}s`}}>
                          <MensaCard mensa={mensa} onFavoriteChange={handleFavoriteChange} />
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Main Mensas */}
                <div>
                  <h3 className="text-2xl font-bold mb-6 text-gray-800">
                    🍽️ Main Dining Halls
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                    {mensas
                      .filter(m => m.info.type === 'mensa' && !favorites.includes(m.key))
                      .map((mensa, index) => (
                        <div key={index} className="animate-slide-up" style={{animationDelay: `${index * 0.1}s`}}>
                          <MensaCard mensa={mensa} onFavoriteChange={handleFavoriteChange} />
                        </div>
                      ))}
                  </div>
                </div>

                {/* Cafeterias */}
                <div>
                  <h3 className="text-2xl font-bold mb-6 text-gray-800">
                    ☕ Cafeterias
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-[1400px] mx-auto">
                    {mensas
                      .filter(m => m.info.type === 'cafeteria' && !favorites.includes(m.key))
                      .map((mensa, index) => (
                        <div key={index} className="animate-slide-up" style={{animationDelay: `${index * 0.1}s`}}>
                          <MensaCard mensa={mensa} onFavoriteChange={handleFavoriteChange} />
                        </div>
                      ))}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Map */}
          <div className="max-w-[1800px] mx-auto mt-16 mb-12 animate-slide-up">
            <div className="glass-strong rounded-2xl p-6">
              <h2 className="text-3xl font-bold mb-6 gradient-text">
                📍 Mensa Locations in Jena
              </h2>
              <Map mensas={mensas} />
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="glass-strong mt-16 py-8">
        <div className="container mx-auto px-4 text-center">
          <p className="text-gray-700 font-semibold">
            Made with <span className="inline-block animate-bounce-slow">☕</span> by{' '}
            <a 
              href="https://kohulanr.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-red-600 hover:text-red-700 font-bold hover:underline transition-colors"
            >
              Kohulan
            </a>{' '}
            at Jena
          </p>
          <p className="text-sm text-gray-600 mt-2">
            Data from Studentenwerk Thüringen | Nutrition from USDA FoodData Central
          </p>
          <p className="text-xs text-gray-500 mt-1">
            All nutritional values are per 100g
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;