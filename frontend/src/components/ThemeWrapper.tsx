'use client';

import { useEffect } from 'react';
import { useTheme } from '@/contexts/ThemeContext';

export default function ThemeWrapper({ children }: { children: React.ReactNode }) {
  const { theme } = useTheme();

  useEffect(() => {
    // Apply theme class to html element
    const html = document.documentElement;
    if (theme === 'dark') {
      html.classList.add('dark');
    } else {
      html.classList.remove('dark');
    }
  }, [theme]);

  return <>{children}</>;
}