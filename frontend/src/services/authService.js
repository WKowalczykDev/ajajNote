import { api } from './api';

export const authService = {
    signup: (data) => api.request('/auth/signup', { method: 'POST', body: data }),
    login: (data) => api.request('/auth/login', { method: 'POST', body: data }),
    logout: () => api.request('/auth/logout', { method: 'POST' }),
    getCurrentUser: () => api.request('/auth/me'),
};