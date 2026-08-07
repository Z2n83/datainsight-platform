import apiClient from './client';
import type { ApiResponse, AnalysisRequest, AnalysisResult } from '@/types';

export async function executeAnalysis(params: AnalysisRequest): Promise<AnalysisResult> {
  const res = await apiClient.post<ApiResponse<AnalysisResult>>('/analysis/execute', params);
  return res.data.data;
}
