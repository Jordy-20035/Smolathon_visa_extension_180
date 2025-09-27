import { api } from './api';
import { 
  LoginResponse, 
  Fine, 
  Accident, 
  TrafficLight, 
  AnalyticsData, 
  DashboardAnalytics,  
  ContentPage,
  ListResponse 
} from '../types';


export class ApiService {
  private static async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
      const token = localStorage.getItem('api_key');
      
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...(token && { 'api-key': token }),
        ...(options.headers as Record<string, string> || {}),
      };
      
      const config: RequestInit = {
        ...options,
        headers,
      };
      
      const response = await fetch(endpoint, config);
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API error (${response.status}): ${errorText}`);
      }
      
      return response.json() as T;
  }

  // Authentication
  static async login(username: string): Promise<LoginResponse> {
    return this.request<LoginResponse>(api.login, {
      method: 'POST',
      body: JSON.stringify({ username }),
    });
  }

  static async getCurrentUser() {
    return this.request(api.getCurrentUser);
  }

  // Data
  static async getFines(params?: Record<string, any>) {
    const queryString = params ? new URLSearchParams(params).toString() : '';
    return this.request(`${api.getFines}?${queryString}`);
  }

  static async getAccidents(params?: Record<string, any>) {
    const queryString = params ? new URLSearchParams(params).toString() : '';
    return this.request(`${api.getAccidents}?${queryString}`);
  }

  // Analytics methods with explicit return types
  static async getDashboardAnalytics(): Promise<DashboardAnalytics> {
    return this.request<DashboardAnalytics>(api.getDashboardAnalytics);
  }

  static async getPublicDashboardAnalytics(): Promise<DashboardAnalytics> {
    return this.request<DashboardAnalytics>(api.getPublicDashboardAnalytics);
  }

  static async getFinesAnalytics(params?: { start_date?: string; end_date?: string; district?: string }): Promise<AnalyticsData> {
    const queryString = params ? new URLSearchParams(params).toString() : '';
    return this.request<AnalyticsData>(`${api.getFinesAnalytics}?${queryString}`);
  }

  static async getAccidentsAnalytics(params?: { start_date?: string; end_date?: string; district?: string }): Promise<AnalyticsData> {
    const queryString = params ? new URLSearchParams(params).toString() : '';
    return this.request<AnalyticsData>(`${api.getAccidentsAnalytics}?${queryString}`);
  }

  static async getTrafficLightsAnalytics(): Promise<{
    total_count: number;
    by_status: Record<string, number>;
    by_district: Record<string, number>;
  }> {
    return this.request(`${api.getTrafficLightsAnalytics}`);
  }


  // Import/Export
  static async importData(modelType: string, file: File, columnMapping: object = {}) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('column_mapping', JSON.stringify(columnMapping));
    
    return this.request(`${api.importData}/${modelType}`, {
      method: 'POST',
      headers: {
        'api-key': localStorage.getItem('api_key') || '',
      },
      body: formData,
    });
  }

  // Content
  static async getNews() {
    return this.request(api.getNews);
  }

  static async getContentPages(pageType?: string) {
    const queryString = pageType ? `?page_type=${pageType}` : '';
    return this.request(`${api.getContentPages}${queryString}`);
  }
}