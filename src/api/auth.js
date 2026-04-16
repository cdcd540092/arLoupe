import axios from 'axios';

const api = axios.create({
    baseURL: '/api/auth',
    headers: {
        'Content-Type': 'application/json'
    }
});

export const login = (credentials) => api.post('/login', credentials);
export const logout = () => api.post('/logout');
export const refreshToken = () => api.post('/refresh');

export default {
    login,
    logout,
    refreshToken
};
