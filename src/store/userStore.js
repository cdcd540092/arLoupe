import { defineStore } from 'pinia';
import auth from '@/api/auth';

export const useUserStore = defineStore('user', {
    state: () => ({
        user: null,
        token: null,
        role: null,
        isAuthenticated: false,
        loading: false,
        error: null
    }),
    getters: {
        isAdmin: (state) => state.role === 'admin',
        isDoctor: (state) => state.role === 'doctor',
        isPatient: (state) => state.role === 'patient'
    },
    actions: {
        setUser(user) {
            this.user = user;
            this.isAuthenticated = !!user;
            
            // Normalize role to lowercase for frontend routing
            let r = user?.role ? user.role.toLowerCase() : null;
            this.role = r;
        },
        setToken(token) {
            this.token = token;
        },
        async login(credentials) {
            this.loading = true;
            this.error = null;
            try {
                // 發送真實請求到後端 API
                const response = await auth.login(credentials);
                // JWT 預設回傳的是 access 與 refresh token，解構出 access 並重新命名為 token
                const { access: token, user } = response.data;

                this.setToken(token);
                this.setUser(user);
                localStorage.setItem('auth_token', token);
                return true;
            } catch (err) {
                console.error("Login failed:", err);
                this.error = err.response?.data?.message || '登入失敗，請確認伺服器連線或帳號密碼。';
                return false;
            } finally {
                this.loading = false;
            }
        },
        logout() {
            this.user = null;
            this.token = null;
            this.role = null;
            this.isAuthenticated = false;
            this.error = null;
            localStorage.removeItem('auth_token');
        }
    }
});
