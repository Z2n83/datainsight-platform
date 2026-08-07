import { create } from 'zustand';
import type { UserInfo } from '@/types';
import { login as loginApi, logout as logoutApi, getMe } from '@/api/auth';

interface AuthState {
  user: UserInfo | null;
  token: string | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  fetchUser: () => Promise<void>;
  initialize: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: localStorage.getItem('access_token'),
  loading: false,

  login: async (username: string, password: string) => {
    set({ loading: true });
    try {
      const data = await loginApi(username, password);
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user_info', JSON.stringify(data.user));
      set({ user: data.user, token: data.access_token, loading: false });
    } catch (error) {
      set({ loading: false });
      throw error;
    }
  },

  logout: async () => {
    try {
      await logoutApi();
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_info');
      set({ user: null, token: null });
    }
  },

  fetchUser: async () => {
    try {
      const user = await getMe();
      set({ user });
      localStorage.setItem('user_info', JSON.stringify(user));
    } catch {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_info');
      set({ user: null, token: null });
    }
  },

  initialize: async () => {
    const token = localStorage.getItem('access_token');
    const cached = localStorage.getItem('user_info');
    if (token && cached) {
      try {
        set({ user: JSON.parse(cached), token });
        // Refresh in background
        get().fetchUser();
      } catch {
        // ignore
      }
    }
  },
}));
