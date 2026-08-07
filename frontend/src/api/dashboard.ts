import apiClient from './client';
import type { ApiResponse, DashboardOverview } from '@/types';

export async function getDashboardOverview(timeRange = '7d'): Promise<DashboardOverview> {
  const res = await apiClient.get<ApiResponse<DashboardOverview>>('/dashboard/overview', {
    params: { time_range: timeRange },
  });
  return res.data.data;
}
