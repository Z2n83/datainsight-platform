import apiClient from './client';
import type { ApiResponse, PaginatedData, Alert, AlertStats } from '@/types';

export async function getAlerts(params: {
  page?: number;
  page_size?: number;
  status?: string;
  level?: string;
}): Promise<PaginatedData<Alert> & { statistics: AlertStats }> {
  const res = await apiClient.get<
    ApiResponse<PaginatedData<Alert> & { statistics: AlertStats }>
  >('/alerts/', { params });
  return res.data.data;
}
