// Base types
export interface User {
  id: string;
  username: string;
  role: string;
  api_key: string;
  created_at: string;
}

export interface Location {
  id: string;
  address: string;
  latitude?: number;
  longitude?: number;
  district?: string;
  created_at: string;
}

export interface Vehicle {
  id: string;
  plate_number: string;
  type?: string;
  created_at: string;
}

export interface Fine {
  id: string;
  vehicle_id: string;
  location_id: string;
  amount: number;
  issued_at: string;
  violation_code?: string;
  status: string;
  visibility: string;
  created_at: string;
  vehicle?: Vehicle;
  location?: Location;
}

export interface Accident {
  id: string;
  location_id: string;
  accident_type: string;
  severity?: string;
  occurred_at: string;
  casualties: number;
  visibility: string;
  created_at: string;
  location?: Location;
}

export interface TrafficLight {
  id: string;
  location_id: string;
  type?: string;
  status: string;
  install_date?: string;
  last_maintenance?: string;
  created_at: string;
  location?: Location;
}

// Analytics types
export interface TimeSeriesPoint {
  date: string;
  count: number;
  amount?: number;
}

export interface AnalyticsData {
  total_count: number;
  total_amount?: number;
  time_series: TimeSeriesPoint[];
  by_district: Record<string, number>;
  by_severity?: Record<string, number>;
  by_type?: Record<string, number>;
}

export interface DashboardAnalytics {
  fines?: {
    total_count: number;
    total_amount?: number;
    time_series: TimeSeriesPoint[];
    by_district: Record<string, number>;
  };
  accidents?: {
    total_count: number;
    time_series: TimeSeriesPoint[];
    by_severity?: Record<string, number>;
    by_type?: Record<string, number>;
  };
  traffic_lights?: {
    total_count: number;
    by_status: Record<string, number>;
    by_district: Record<string, number>;
  };
}

// Content types
export interface ContentPage {
  id: string;
  title: string;
  slug: string;
  content: string;
  is_published: boolean;
  page_type: string;
  author_id: string;
  created_at: string;
  updated_at: string;
}

// API response types
export interface LoginResponse {
  username: string;
  api_key: string;
  role: string;
}

export interface ListResponse<T> {
  items: T[];
  total: number;
  page?: number;
  per_page?: number;
  pages?: number;
}