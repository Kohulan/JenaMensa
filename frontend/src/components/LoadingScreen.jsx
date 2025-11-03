import { useState, useEffect } from 'react';

const LoadingScreen = ({ loadingProgress = 0, loadingMessage = '' }) => {
  const [dots, setDots] = useState('');

  // Loading steps with fun messages - will be controlled by parent
  const steps = [
    { icon: '🔍', message: 'Connecting to server', color: 'text-blue-600' },
    { icon: '🍽️', message: 'Fetching today\'s menu', color: 'text-green-600' },
    { icon: '🥗', message: 'Loading meal information', color: 'text-emerald-600' },
    { icon: '💰', message: 'Getting prices & nutrition', color: 'text-yellow-600' },
    { icon: '🗺️', message: 'Preparing locations', color: 'text-red-600' },
    { icon: '✨', message: 'Almost ready', color: 'text-purple-600' },
  ];

  // Determine current step based on progress
  const currentStep = Math.min(
    Math.floor((loadingProgress / 100) * steps.length),
    steps.length - 1
  );

  // Animate dots
  useEffect(() => {
    const dotInterval = setInterval(() => {
      setDots((prev) => (prev.length >= 3 ? '' : prev + '.'));
    }, 400);

    return () => clearInterval(dotInterval);
  }, []);

  // Food emojis floating around
  const floatingFoods = ['🍕', '🍔', '🍜', '🥘', '🍱', '🥗', '🍝', '🥙', '🌮', '🍲'];

  return (
    <div className="text-center py-20 relative overflow-hidden">
      {/* Floating food emojis in background */}
      <div className="absolute inset-0 pointer-events-none">
        {floatingFoods.map((food, index) => (
          <div
            key={index}
            className="absolute text-4xl opacity-20 animate-float"
            style={{
              left: `${(index * 10) % 90}%`,
              top: `${(index * 15) % 80}%`,
              animationDelay: `${index * 0.3}s`,
              animationDuration: `${4 + (index % 3)}s`,
            }}
          >
            {food}
          </div>
        ))}
      </div>

      {/* Main loading content */}
      <div className="relative z-10">
        {/* Main spinner with chef hat */}
        <div className="flex justify-center items-center mb-8">
          <div className="relative">
            {/* Outer spinning circle */}
            <div className="w-24 h-24 border-8 border-red-200 border-t-red-600 rounded-full animate-spin"></div>
            
            {/* Inner pulsing circle */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-16 h-16 bg-gradient-to-br from-red-100 to-rose-100 rounded-full animate-pulse-slow flex items-center justify-center">
                <span className="text-3xl animate-bounce-slow">👨‍🍳</span>
              </div>
            </div>

            {/* Ping effect */}
            <div className="absolute inset-0 animate-ping-slow">
              <div className="w-24 h-24 bg-red-400 rounded-full opacity-20"></div>
            </div>
          </div>
        </div>

        {/* Loading message with icon */}
        <div className="glass-strong inline-block px-8 py-6 rounded-2xl mb-6 min-w-[350px]">
          <div className="flex items-center justify-center gap-3 mb-3">
            <span className={`text-5xl animate-wiggle ${steps[currentStep].color}`}>
              {steps[currentStep].icon}
            </span>
          </div>
          
          <p className={`text-xl font-bold ${steps[currentStep].color} transition-all duration-300`}>
            {loadingMessage || steps[currentStep].message}{dots}
          </p>
        </div>

        {/* Progress indicator */}
        <div className="max-w-md mx-auto">
          <div className="bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-red-500 via-rose-500 to-red-600 transition-all duration-500 ease-out rounded-full"
              style={{
                width: `${loadingProgress}%`,
              }}
            >
              <div className="w-full h-full animate-pulse-slow bg-gradient-to-r from-transparent via-white/30 to-transparent"></div>
            </div>
          </div>
          
          {/* Progress percentage */}
          <p className="text-sm text-gray-600 mt-3 font-medium">
            {loadingProgress}% Complete
          </p>
        </div>

        {/* Fun additional message */}
        <div className="mt-8 animate-fade-in">
          <p className="text-gray-600 text-lg font-medium">
            🎉 Preparing your personalized dining experience
          </p>
        </div>

        {/* Mini food icons cycling */}
        <div className="flex justify-center gap-3 mt-6">
          {['🍽️', '🥄', '🍴'].map((icon, index) => (
            <span
              key={index}
              className="text-2xl opacity-50 animate-bounce-slow"
              style={{ animationDelay: `${index * 0.2}s` }}
            >
              {icon}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default LoadingScreen;
