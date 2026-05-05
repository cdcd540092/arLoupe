import axios from 'axios';

const api = axios.create({
    baseURL: '/api/audit',
});

export const getAuditLogs = (params) => api.get('/logs', { params });
export const exportLogs = () => api.get('/export', { responseType: 'blob' });

export default {
    getAuditLogs,
    exportLogs
};
