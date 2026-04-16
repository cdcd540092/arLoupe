import { defineStore } from 'pinia';
import en from '@/i18n/en';
import zh from '@/i18n/zh';

const messages = { en, zh };

export const useLangStore = defineStore('lang', {
    state: () => ({
        locale: 'zh'
    }),
    getters: {
        t: (state) => messages[state.locale],
        isZh: (state) => state.locale === 'zh'
    },
    actions: {
        toggle() {
            this.locale = this.locale === 'en' ? 'zh' : 'en';
        },
        setLocale(locale) {
            this.locale = locale;
        }
    }
});
