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

// Request interceptor — attach Bearer token if present and valid
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('routeiq_token');
    if (token && token !== 'undefined' && token !== 'null') {
      config.headers.Authorization = `Bearer ${token}`;
    }
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
  getTamilCalendar: (params) => api.get('/events/tamil-calendar', { params }),
  activateTamilEvent: (data) => api.post('/events/tamil-calendar/activate', data),
  create: (data) => api.post('/events', data),
  update: (id, data) => api.put(`/events/${id}`, data),
  delete: (id) => api.delete(`/events/${id}`),
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
  forecastEvaluations: (params) => api.get('/admin/forecast-evaluations', { params }),
  forecastMetrics: () => api.get('/admin/forecast-evaluations/metrics'),
  forecastTable: (limit = 100) => api.get('/admin/forecast-evaluations/table', { params: { limit } }),
  runAMPrediction: (targetDate) => api.post('/admin/forecast-evaluations/run-8am', { target_date: targetDate }),
  collectPMActuals: (targetDate) => api.post('/admin/forecast-evaluations/collect-5pm', { target_date: targetDate }),
  runDailyCheck: (targetDate) => api.post('/admin/forecast-evaluations/run-daily-check', { target_date: targetDate }),
  getPredictionsList: (params) => api.get('/admin/predictions-list', { params }),
  getReportsSummary: (params) => api.get('/admin/reports/summary', { params }),
  reportsSummary: (params) => api.get('/admin/reports/summary', { params }),
  getApiStatus: () => api.get('/admin/api-status'),
  apiStatus: () => api.get('/admin/api-status'),
  triggerSchedulerJob: (jobId) => api.post('/admin/scheduler/trigger-job', { job_id: jobId }),
  getTraffic: (params) => api.get('/admin/traffic', { params }),
  addTraffic: (data) => api.post('/admin/traffic', data),
  updateTraffic: (id, data) => api.put(`/admin/traffic/${id}`, data),
  deleteTraffic: (id) => api.delete(`/admin/traffic/${id}`),
};

export const userApi = {
  stats: () => api.get('/user/stats'),
  getStats: () => api.get('/user/stats'),
  history: (params) => api.get('/user/history', { params }),
  getHistory: (params) => api.get('/user/history', { params }),
  recommended: (params) => api.get('/user/recommended', { params }),
  getRecommended: (params) => api.get('/user/recommended', { params }),
};

export const favoritesApi = {
  list: () => api.get('/favorites'),
  getFavorites: () => api.get('/favorites'),
  add: (data) => api.post('/favorites', data),
  addFavorite: (data) => api.post('/favorites', data),
  remove: (id) => api.delete(`/favorites/${id}`),
  removeFavorite: (id) => api.delete(`/favorites/${id}`),
};

export const authApi = {
  me: () => api.get('/auth/me'),
  getMe: () => api.get('/auth/me'),
  updateProfile: (data) => api.put('/auth/profile', data),
  changePassword: (data) => api.post('/auth/change-password', data),
  forgotPassword: (data) => api.post('/auth/forgot-password', data),
  resetPassword: (data) => api.post('/auth/reset-password', data),
};
