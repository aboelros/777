import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useThemeStore = create(
    persist(
        (set) => ({
            theme: 'dark-modern', // dark-modern, dark-elegance, light-classic, light-vibrant
            language: 'en', // en, ar

            setTheme: (theme) => {
                set({ theme });
                // Apply theme class to body
                document.body.className = '';
                if (theme !== 'dark-modern') {
                    document.body.classList.add(`theme-${theme}`);
                }
            },

            setLanguage: (language) => {
                set({ language });
                document.documentElement.dir = language === 'ar' ? 'rtl' : 'ltr';
                document.documentElement.lang = language;
            },

            initialize: () => {
                // Determine logic on hydration if needed
                const state = useThemeStore.getState();

                // Apply Theme
                document.body.className = '';
                if (state.theme !== 'dark-modern') {
                    document.body.classList.add(`theme-${state.theme}`);
                }

                // Apply Language
                document.documentElement.dir = state.language === 'ar' ? 'rtl' : 'ltr';
                document.documentElement.lang = state.language;
            }
        }),
        {
            name: 'ui-preference-storage',
        }
    )
);

export default useThemeStore;
