import axios from 'axios';
import { useUserStore } from '@/store/userStore';

// We import router lazily or use window.location to avoid circular dependencies if needed.
// It's safer to just do window.location.href or inject router.

const api = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json'
    }
});

// Request interceptor to attach JWT token
api.interceptors.request.use(config => {
    const token = localStorage.getItem('auth_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}, error => {
    return Promise.reject(error);
});

// Response interceptor to handle 401 Unauthorized
api.interceptors.response.use(response => {
    return response;
}, error => {
    if (error.response && error.response.status === 401) {
        // Token is invalid or expired
        const userStore = useUserStore();
        userStore.logout();
        
        // Only redirect to login if we are not already on the login page
        if (window.location.pathname !== '/login') {
            window.location.href = '/login';
        }
    }
    return Promise.reject(error);
});

export default api;
