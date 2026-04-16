import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', {
    state: () => ({
        user: null,
        token: null,
        role: null,
        isAuthenticated: false
    }),
    getters: {
        isAdmin: (state) => state.role === 'admin',
        isStaff: (state) => state.role === 'staff',
        isPatient: (state) => state.role === 'patient'
    },
    actions: {
        setUser(user) {
            this.user = user;
            this.isAuthenticated = !!user;
            this.role = user?.role || null;
        },
        setToken(token) {
            this.token = token;
        },
        logout() {
            this.user = null;
            this.token = null;
            this.role = null;
            this.isAuthenticated = false;
        }
    }
});
