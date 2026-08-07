import apiClient from './client';
import type { ApiResponse, LoginResponse, UserInfo } from '@/types';

export async function login(username: string, password: string): Promise<LoginResponse> {
  const res = await apiClient.post<ApiResponse<LoginResponse>>('/auth/login', {
    username,
    password,
  });
  return res.data.data;
}

export async function logout(): Promise<void> {
  await apiClient.post('/auth/logout');
}

export async function getMe(): Promise<UserInfo> {
  const res = await apiClient.get<ApiResponse<UserInfo>>('/auth/me');
  return res.data.data;
}
