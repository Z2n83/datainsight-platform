import apiClient from './client';
import type { ApiResponse, PaginatedData, Dataset } from '@/types';

export async function getDatasets(params: {
  page?: number;
  page_size?: number;
  keyword?: string;
  source_id?: string;
}): Promise<PaginatedData<Dataset>> {
  const res = await apiClient.get<ApiResponse<PaginatedData<Dataset>>>('/datasets/', { params });
  return res.data.data;
}

export async function getDataset(id: string): Promise<Dataset> {
  const res = await apiClient.get<ApiResponse<Dataset>>(`/datasets/${id}`);
  return res.data.data;
}
