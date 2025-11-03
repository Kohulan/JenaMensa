function MealItem({ meal }) {
  const hasNutrition = meal.nutrition && meal.nutrition.calories;

  return (
    <div className="glass rounded-xl p-4 hover:bg-white hover:border-red-300 transition-all duration-300">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <h5 className="font-bold text-gray-800 mb-1">
            {meal.name}
          </h5>
          
          {meal.category && (
            <p className="text-xs text-gray-600 mb-2">
              {meal.category}
            </p>
          )}

          {/* Prices */}
          {(meal.price_student && meal.price_student !== 'N/A') && (
            <div className="inline-block bg-gradient-to-r from-red-50 to-orange-50 border border-red-200 px-3 py-2 rounded-lg">
              <div className="flex items-center gap-3">
                <span className="text-xl">💰</span>
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-600 w-16">Student:</span>
                    <span className="text-sm font-bold text-red-700">€{meal.price_student}</span>
                  </div>
                  {meal.price_employee && meal.price_employee !== 'N/A' && (
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-600 w-16">Staff:</span>
                      <span className="text-sm font-semibold text-red-600">€{meal.price_employee}</span>
                    </div>
                  )}
                  {meal.price_guest && meal.price_guest !== 'N/A' && (
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-600 w-16">Guest:</span>
                      <span className="text-sm font-semibold text-red-500">€{meal.price_guest}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Nutrition Info */}
        {hasNutrition && (
          <div className="bg-gradient-to-br from-orange-50 to-red-50 border border-orange-200 rounded-lg p-3 min-w-[120px]">
            <p className="text-2xl font-bold text-orange-600 text-center mb-1">
              {meal.nutrition.calories}
            </p>
            <p className="text-xs text-gray-600 text-center font-semibold">
              kcal / 100g
            </p>
            
            {/* Macros */}
            {(meal.nutrition.protein || meal.nutrition.carbs || meal.nutrition.fat) && (
              <div className="mt-2 pt-2 border-t border-orange-200 space-y-1">
                {meal.nutrition.protein && (
                  <p className="text-xs text-gray-600">
                    Protein: <span className="font-semibold">{meal.nutrition.protein}g</span>
                  </p>
                )}
                {meal.nutrition.carbs && (
                  <p className="text-xs text-gray-600">
                    Carbs: <span className="font-semibold">{meal.nutrition.carbs}g</span>
                  </p>
                )}
                {meal.nutrition.fat && (
                  <p className="text-xs text-gray-600">
                    Fat: <span className="font-semibold">{meal.nutrition.fat}g</span>
                  </p>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* CO2 Equivalent */}
      {meal.co2_equivalent && (
        <div className="mt-3 inline-flex items-center gap-2 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 px-3 py-2 rounded-lg">
          <span className="text-lg">🌍</span>
          <div>
            <p className="text-sm font-bold text-green-700">
              {meal.co2_equivalent}g CO₂
            </p>
            <p className="text-xs text-green-600">
              per portion
            </p>
          </div>
        </div>
      )}

      {/* Original German Name */}
      {meal.name_original && meal.name_original !== meal.name && (
        <div className="mt-3 pt-3 border-t border-red-100">
          <p className="text-xs text-gray-500">
            🇩🇪 Original: {meal.name_original}
          </p>
        </div>
      )}
    </div>
  );
}

export default MealItem;