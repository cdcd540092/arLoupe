import { defineStore } from 'pinia';

export const useThemeStore = defineStore('theme', {
    state: () => ({
        isDark: false
    }),
    actions: {
        toggle() {
            this.isDark = !this.isDark;
            this.applyTheme();
        },
        applyTheme() {
            if (this.isDark) {
                document.documentElement.classList.add('dark');
            } else {
                document.documentElement.classList.remove('dark');
            }
        },
        init() {
            // Check system preference on first load
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            this.isDark = prefersDark;
            this.applyTheme();
        }
    }
});
