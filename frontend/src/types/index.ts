// ---- API Response ----
export interface ApiResponse<T = unknown> {
  code: number;
  message: string;
  data: T;
}

export interface PaginatedData<T> {
  list: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// ---- Auth ----
export interface UserInfo {
  id: string;
  username: string;
  real_name: string;
  email: string | null;
  phone: string | null;
  avatar_url: string | null;
  roles: { id: string; name: string; description: string | null }[];
  permissions: string[];
  last_login_at: string | null;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: UserInfo;
}

// ---- Dashboard ----
export interface KpiItem {
  label: string;
  value: number;
  unit: string;
  trend: number;
  trend_label: string;
}

export interface TrendPoint {
  date: string;
  value: number;
  count?: number;
}

export interface StatusDistribution {
  status: string;
  count: number;
  percentage: number;
}

export interface RecentAlert {
  id: string;
  title: string;
  level: string;
  triggered_at: string;
}

export interface TodoSection {
  pending_alerts: number;
  pending_inspections: number;
  data_source_errors: number;
  data_quality_issues: number;
}

export interface DashboardOverview {
  kpi: KpiItem[];
  data_volume_trend: TrendPoint[];
  device_status_distribution: StatusDistribution[];
  anomaly_trend: TrendPoint[];
  todos: TodoSection;
  recent_alerts: RecentAlert[];
}

// ---- Data Source ----
export interface DataSource {
  id: string;
  name: string;
  type: string;
  description: string | null;
  status: string;
  data_volume: number;
  sync_method: string;
  sync_frequency: string | null;
  last_sync_at: string | null;
  last_sync_status: string | null;
  owner: { id: string; real_name: string } | null;
  created_at: string;
  updated_at: string;
}

// ---- Dataset ----
export interface DatasetField {
  id: string;
  field_name: string;
  field_alias: string | null;
  field_type: string;
  is_dimension: boolean;
  is_metric: boolean;
  aggregation: string | null;
  unit: string | null;
  sort_order: number;
}

export interface Dataset {
  id: string;
  name: string;
  description: string | null;
  source: { id: string; name: string } | null;
  source_table: string;
  field_count: number;
  data_volume: number;
  last_refresh_at: string | null;
  owner: { id: string; real_name: string } | null;
  fields: DatasetField[];
  created_at: string;
  updated_at: string;
}

// ---- Analysis ----
export interface AnalysisRequest {
  dataset_id: string;
  metrics: { field_name: string; aggregation: string }[];
  dimensions?: string[];
  time_range?: { start?: string; end?: string; preset?: string };
  granularity?: string;
  filters?: { field: string; operator: string; value: unknown }[];
  analysis_type?: string;
  limit?: number;
}

export interface AnalysisResult {
  chart_data: Record<string, unknown>[];
  summary: {
    avg: number | null;
    max: number | null;
    min: number | null;
    trend: string | null;
    change_rate: number | null;
  };
  insights: string[];
  table_data: { columns: string[]; rows: unknown[][] };
  execution_time_ms: number;
}

// ---- Alert ----
export interface Alert {
  id: string;
  title: string;
  description: string | null;
  level: string;
  status: string;
  current_value: number;
  threshold_value: number;
  triggered_at: string;
  rule: { id: string; name: string } | null;
  assignee: { id: string; real_name: string } | null;
  processed_at: string | null;
  closed_at: string | null;
}

export interface AlertStats {
  critical: number;
  high: number;
  medium: number;
  low: number;
}
