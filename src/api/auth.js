import api from './index';

export const login = (credentials) => api.post('/auth/login/', credentials);
export const logout = () => api.post('/auth/logout/');
export const refreshToken = () => api.post('/auth/token/refresh/');

export default {
    login,
    logout,
    refreshToken
};
