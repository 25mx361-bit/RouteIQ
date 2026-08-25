/**
 * frontend/src/services/api.js
 * Centralised Axios instance for RouteIQ.
 * Injects auth token (from localStorage) on every request via interceptor.
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

// Request interceptor — attach Bearer token if present
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('routeiq_token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor — surface structured error messages
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.message ||
      error.response?.data?.error ||
      error.message ||
      'An unexpected error occurred.';
    return Promise.reject(new Error(message));
  }
);

export default api;

// ── Named API helpers ────────────────────────────────────────────────────────

export const geocodeApi = {
  search: (query) => api.get('/geocode/search', { params: { q: query } }),
  reverse: (lat, lng) => api.get('/geocode/reverse', { params: { lat, lng } }),
};

export const routesApi = {
  search: (payload) => api.post('/routes/search', payload),
};

export const trafficApi = {
  routeFlow: (coordinates) => api.post('/traffic/route-flow', { coordinates }),
};

export const weatherApi = {
  current: (lat, lng) => api.get('/weather/current', { params: { lat, lng } }),
  forecast: (lat, lng, date, time) =>
    api.get('/weather/forecast', { params: { lat, lng, date, time } }),
};

export const eventsApi = {
  list: (params) => api.get('/events', { params }),
  routeImpact: (coordinates, datetime) =>
    api.post('/events/route-impact', { coordinates, datetime }),
};

export const landslideApi = {
  list: (params) => api.get('/landslides', { params }),
  checkRoute: (coordinates) => api.post('/landslides/check-route', { coordinates }),
};

export const notificationsApi = {
  list: (userId, unreadOnly = false) =>
    api.get('/notifications', { params: { user_id: userId, unread_only: unreadOnly } }),
  markRead: (id, userId) =>
    api.put(`/notifications/${id}/read`, null, { params: { user_id: userId } }),
  markAllRead: (userId) =>
    api.put('/notifications/read-all', null, { params: { user_id: userId } }),
};

export const adminApi = {
  catboostTrain: () => api.post('/admin/models/catboost/train'),
  catboostMetrics: () => api.get('/admin/models/catboost/metrics'),
  patchtstTrain: () => api.post('/admin/models/patchtst/train'),
  patchtstMetrics: () => api.get('/admin/models/patchtst/metrics'),
  schedulerStatus: () => api.get('/admin/scheduler/status'),
  stats: () => api.get('/admin/stats'),
  users: (params) => api.get('/admin/users', { params }),
  updateRole: (userId, role) => api.put(`/admin/users/${userId}/role`, { role }),
  deactivateUser: (userId) => api.put(`/admin/users/${userId}/deactivate`),
  logs: (params) => api.get('/admin/logs', { params }),
};
