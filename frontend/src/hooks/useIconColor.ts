import { useTheme } from '@/context/ThemeContext'

/**
 * Hook to get theme-aware icon colors
 * Returns color values that can be passed directly to lucide-react icon components
 */
export function useIconColor() {
  const { theme } = useTheme()

  return {
    // Primary foreground color
    foreground: theme === 'dark' ? 'hsl(210 40% 98%)' : 'hsl(222.2 84% 4.9%)',
    
    // Muted/secondary color
    muted: theme === 'dark' ? 'hsl(215 20.2% 65.1%)' : 'hsl(215.4 16.3% 46.9%)',
    
    // Primary accent color
    primary: theme === 'dark' ? 'hsl(210 40% 98%)' : 'hsl(222.2 47.4% 11.2%)',
    
    // Destructive/error color
    destructive: theme === 'dark' ? 'hsl(0 62.8% 30.6%)' : 'hsl(0 84.2% 60.2%)',
    
    // Success color
    success: theme === 'dark' ? 'hsl(142 76% 36%)' : 'hsl(142 71% 45%)',
    
    // Warning color
    warning: theme === 'dark' ? 'hsl(48 96% 53%)' : 'hsl(48 96% 53%)',
    
    // Current theme
    theme,
  }
}
