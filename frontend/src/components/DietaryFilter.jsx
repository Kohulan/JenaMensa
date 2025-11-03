function DietaryFilter({ dietaryRequirements, setDietaryRequirements, onGetSuggestions }) {
  const dietaryOptions = [
    { value: 'vegetarian', label: '🥗 Vegetarian', color: 'green' },
    { value: 'vegan', label: '🌱 Vegan', color: 'emerald' },
    { value: 'meat', label: '🍖 Meat', color: 'red' },
    { value: 'halal', label: '🕌 Halal', color: 'blue' },
    { value: 'gluten-free', label: '🌾 Gluten-Free', color: 'yellow' },
    { value: 'lactose-free', label: '🥛 Lactose-Free', color: 'purple' }
  ];

  const toggleDietaryRequirement = (value) => {
    if (dietaryRequirements.includes(value)) {
      setDietaryRequirements(dietaryRequirements.filter(req => req !== value));
    } else {
      setDietaryRequirements([...dietaryRequirements, value]);
    }
  };

  const getButtonClasses = (option) => {
    const isSelected = dietaryRequirements.includes(option.value);
    
    if (!isSelected) {
      return 'glass hover:bg-white/50 text-gray-800';
    }
    
    // Selected state with explicit classes
    const colorClasses = {
      green: 'bg-green-500 text-white shadow-lg',
      emerald: 'bg-emerald-500 text-white shadow-lg',
      red: 'bg-red-500 text-white shadow-lg',
      blue: 'bg-blue-500 text-white shadow-lg',
      yellow: 'bg-yellow-500 text-white shadow-lg',
      purple: 'bg-purple-500 text-white shadow-lg'
    };
    
    return colorClasses[option.color] || 'bg-gray-500 text-white shadow-lg';
  };

  return (
    <div className="glass-strong rounded-2xl p-8">
      <h2 className="text-2xl font-bold mb-4 gradient-text">
        🍽️ Dietary Preferences
      </h2>
      <p className="text-gray-600 mb-6">
        Select your dietary requirements to get personalized mensa recommendations
      </p>

      <div className="flex flex-wrap lg:flex-nowrap gap-3 mb-6 justify-center lg:justify-start">
        {dietaryOptions.map((option) => (
          <button
            key={option.value}
            onClick={() => toggleDietaryRequirement(option.value)}
            className={`px-6 py-3 rounded-xl font-semibold transition-all duration-300 transform hover:scale-105 ${getButtonClasses(option)}`}
          >
            {option.label}
          </button>
        ))}
      </div>

      {dietaryRequirements.length > 0 && (
        <div className="flex items-center gap-4">
          <div className="flex-1 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-sm font-semibold text-red-800">
              Selected: {dietaryRequirements.join(', ')}
            </p>
          </div>
          <button
            onClick={onGetSuggestions}
            className="btn-primary whitespace-nowrap"
          >
            Get Recommendations 🎯
          </button>
        </div>
      )}
    </div>
  );
}

export default DietaryFilter;