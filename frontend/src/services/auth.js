/**
 * frontend/src/services/auth.js
 * JWT token helpers — single source of truth for auth state.
 */

const TOKEN_KEY = 'routeiq_token';
const USER_KEY  = 'routeiq_user';

export function setSession(token, user) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new Event('authChange'));
  }
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new Event('authChange'));
  }
}

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function getUser() {
  try {
    return JSON.parse(localStorage.getItem(USER_KEY));
  } catch {
    return null;
  }
}

export function isLoggedIn() {
  return !!getToken();
}

export function isAdmin() {
  return getUser()?.role === 'admin';
}
