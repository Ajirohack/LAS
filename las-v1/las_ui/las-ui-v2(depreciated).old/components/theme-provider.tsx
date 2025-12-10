"use client"

import { createContext, useContext, useEffect, useState } from 'react'

type Theme = 'dark' | 'light' | 'system'

interface ThemeContextType {
    theme: Theme
    setTheme: (theme: Theme) => void
    actualTheme: 'dark' | 'light'
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function ThemeProvider({ children }: { children: React.ReactNode }) {
    const [theme, setThemeState] = useState<Theme>('dark')
    const [actualTheme, setActualTheme] = useState<'dark' | 'light'>('dark')

    useEffect(() => {
        // Load theme from API on mount
        fetch('/api/preferences/theme')
            .then(res => res.json())
            .then(data => {
                if (data.theme) {
                    setThemeState(data.theme)
                }
            })
            .catch(() => {
                // Fallback to localStorage
                const stored = localStorage.getItem('theme') as Theme
                if (stored) setThemeState(stored)
            })
    }, [])

    useEffect(() => {
        // Determine actual theme
        let resolved: 'dark' | 'light' = 'dark'

        if (theme === 'system') {
            resolved = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
        } else {
            resolved = theme as 'dark' | 'light'
        }

        setActualTheme(resolved)

        // Apply theme to document
        document.documentElement.setAttribute('data-theme', resolved)
        document.documentElement.classList.remove('light', 'dark')
        document.documentElement.classList.add(resolved)
    }, [theme])

    const setTheme = (newTheme: Theme) => {
        setThemeState(newTheme)

        // Save to API
        fetch('/api/preferences/theme', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ theme: newTheme })
        }).catch(() => {
            // Fallback to localStorage
            localStorage.setItem('theme', newTheme)
        })
    }

    return (
        <ThemeContext.Provider value={{ theme, setTheme, actualTheme }}>
            {children}
        </ThemeContext.Provider>
    )
}

export function useTheme() {
    const context = useContext(ThemeContext)
    if (!context) {
        throw new Error('useTheme must be used within ThemeProvider')
    }
    return context
}
