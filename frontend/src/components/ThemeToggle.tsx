'use client';

import { Moon, Sun } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 transition-all duration-300 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-white dark:focus:ring-offset-gray-800 transform hover:scale-105 active:scale-95"
      aria-label="Toggle theme"
      title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
    >
      <div className="relative">
        {theme === 'light' ? (
          <Moon className="h-5 w-5 text-gray-700 dark:text-gray-300 transition-all duration-300" />
        ) : (
          <Sun className="h-5 w-5 text-yellow-500 dark:text-yellow-400 transition-all duration-300" />
        )}
      </div>
    </button>
  );
}
