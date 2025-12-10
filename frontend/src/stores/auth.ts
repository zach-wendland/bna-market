import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '@/api/client';

export interface User {
  id: string;
  email: string;
  role?: string;
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null);
  const accessToken = ref<string | null>(null);
  const refreshToken = ref<string | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // Computed
  const isAuthenticated = computed(() => !!user.value && !!accessToken.value);

  // Actions
  async function sendMagicLink(email: string, redirectTo?: string): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      await api.post('/auth/magic-link', {
        email,
        redirectTo: redirectTo || `${window.location.origin}/auth/callback`
      });
    } catch (e: any) {
      const errorMessage = e.response?.data?.error || e.message || 'Failed to send magic link';
      error.value = errorMessage;
      throw new Error(errorMessage);
    } finally {
      isLoading.value = false;
    }
  }

  async function handleMagicLinkCallback(access_token: string, refresh_token: string): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      // Store tokens from Supabase (already verified)
      accessToken.value = access_token;
      refreshToken.value = refresh_token;

      // Store in localStorage for persistence
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);

      // Set default auth header for future requests
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

      // Get user info from our backend
      const response = await api.get('/auth/session');
      user.value = response.data.user;
      localStorage.setItem('user', JSON.stringify(response.data.user));

      console.log('User authenticated:', user.value);
    } catch (e: any) {
      const errorMessage = e.response?.data?.error || e.message || 'Failed to complete authentication';
      error.value = errorMessage;
      throw new Error(errorMessage);
    } finally {
      isLoading.value = false;
    }
  }

  async function loadSession(): Promise<void> {
    // Load from localStorage on app init
    const token = localStorage.getItem('access_token');
    const userStr = localStorage.getItem('user');

    if (token && userStr) {
      accessToken.value = token;
      refreshToken.value = localStorage.getItem('refresh_token');
      user.value = JSON.parse(userStr);
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;

      // Verify session is still valid
      try {
        const response = await api.get('/auth/session');
        // Update user info in case it changed
        user.value = response.data.user;
      } catch (e) {
        console.warn('Session expired or invalid, logging out');
        // Session expired, clear state
        await logout();
      }
    }
  }

  async function refreshAccessToken(): Promise<void> {
    if (!refreshToken.value) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await api.post('/auth/refresh', {
        refresh_token: refreshToken.value
      });

      accessToken.value = response.data.access_token;
      refreshToken.value = response.data.refresh_token;

      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);

      api.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`;

      console.log('Token refreshed successfully');
    } catch (e: any) {
      console.error('Token refresh failed:', e);
      // Refresh failed, log out user
      await logout();
      throw new Error('Session expired. Please log in again.');
    }
  }

  async function logout(): Promise<void> {
    try {
      if (accessToken.value) {
        await api.post('/auth/logout');
      }
    } catch (e) {
      console.error('Logout API call failed:', e);
    } finally {
      // Clear state regardless of API call success
      user.value = null;
      accessToken.value = null;
      refreshToken.value = null;
      error.value = null;

      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');

      delete api.defaults.headers.common['Authorization'];

      console.log('User logged out');
    }
  }

  function clearError(): void {
    error.value = null;
  }

  return {
    // State
    user,
    accessToken,
    refreshToken,
    isLoading,
    error,

    // Computed
    isAuthenticated,

    // Actions
    sendMagicLink,
    handleMagicLinkCallback,
    loadSession,
    refreshAccessToken,
    logout,
    clearError
  };
});
