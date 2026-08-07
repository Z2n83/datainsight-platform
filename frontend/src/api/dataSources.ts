import apiClient from './client';
import type { ApiResponse, PaginatedData, DataSource } from '@/types';

export async function getDataSources(params: {
  page?: number;
  page_size?: number;
  keyword?: string;
  type?: string;
  status?: string;
}): Promise<PaginatedData<DataSource>> {
  const res = await apiClient.get<ApiResponse<PaginatedData<DataSource>>>('/data-sources/', { params });
  return res.data.data;
}

export async function getDataSource(id: string): Promise<DataSource> {
  const res = await apiClient.get<ApiResponse<DataSource>>(`/data-sources/${id}`);
  return res.data.data;
}

export async function createDataSource(data: Record<string, unknown>): Promise<DataSource> {
  const res = await apiClient.post<ApiResponse<DataSource>>('/data-sources/', data);
  return res.data.data;
}

export async function testConnection(id: string): Promise<{ success: boolean; latency_ms?: number; message: string }> {
  const res = await apiClient.post<ApiResponse<{ success: boolean; latency_ms?: number; message: string }>>(`/data-sources/${id}/test`);
  return res.data.data;
}

export async function triggerSync(id: string): Promise<{ sync_log_id: string; status: string; message: string }> {
  const res = await apiClient.post<ApiResponse<{ sync_log_id: string; status: string; message: string }>>(`/data-sources/${id}/sync`);
  return res.data.data;
}
