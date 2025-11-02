import { api } from './api';
import axios from "axios";
import { 
  LoginResponse, 
  Fine, 
  Accident, 
  TrafficLight, 
  AnalyticsData, 
  DashboardAnalytics,  
  ContentPage,
  ListResponse,
  ContentPageCreate,  
  ContentPageUpdate,  
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

  static async getAdminContentPages(page: number = 1, perPage: number = 20) {
    return this.request(`${api.adminContentPages}?page=${page}&per_page=${perPage}`);
  }

  static async getContentPageById(id: string) {
    return this.request(api.contentPage(id));
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

// Add to services.ts
  static async getEvacuationsAnalytics(params?: { start_date?: string; end_date?: string }): Promise<any> {
    const queryString = params ? new URLSearchParams(params).toString() : '';
    return this.request(`${api.getEvacuationsAnalytics}?${queryString}`);
  }  


  // Import/Export 
// In services.ts - fix the getColumnMappings method
  static async getColumnMappings(modelType: string) {
    const token = localStorage.getItem('api_key');
    const headers: Record<string, string> = {
      ...(token && { 'api-key': token }),
    };
    
    const res = await axios.get(api.getColumnMappings(modelType), { headers });
    return res.data;
  }

  static async importData(modelType: string, file: File, columnMappings: Record<string, string>) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("column_mappings", JSON.stringify(columnMappings));
    
    const token = localStorage.getItem('api_key');
    const headers: Record<string, string> = {
      "Content-Type": "multipart/form-data",
      ...(token && { 'api-key': token }),
    };
    
    const res = await axios.post(api.importData(modelType), formData, {
      headers,
    });
    return res.data;
  }

  // Add export method - UPDATED
  static async exportData(exportType: string, format: string = 'csv') {
    const token = localStorage.getItem('api_key');
    const response = await fetch(`${api.exportData(exportType)}?format=${format}`, {
      headers: {
        'api-key': token || '',
      },
    });
    
    if (!response.ok) {
      throw new Error(`Export failed: ${response.statusText}`);
    }
    
    return response.blob();
  }


// Content Management Methods
  static async getContentPages(pageType?: string): Promise<ContentPage[]> {
    const queryString = pageType ? `?page_type=${pageType}` : '';
    return this.request<ContentPage[]>(`${api.getContentPages}${queryString}`);
  }

  static async createPage(pageData: ContentPageCreate): Promise<ContentPage> {
    return this.request<ContentPage>(api.getContentPages, {
      method: 'POST',
      body: JSON.stringify(pageData),
    });
  }

  static async updatePage(pageId: string, updates: ContentPageUpdate): Promise<ContentPage> {
    return this.request<ContentPage>(`${api.getContentPages}/${pageId}`, {
      method: 'PUT', 
      body: JSON.stringify(updates),
    });
  }

  static async deletePage(pageId: string): Promise<void> {
    return this.request(`${api.getContentPages}/${pageId}`, {
      method: 'DELETE',
    });
  }

  // Traffic Analysis Methods
  static async analyzeJointMovement(params: {
    target_vehicle_id: string;
    min_common_nodes?: number;
    max_time_gap_seconds?: number;
    max_lead_seconds?: number;
    start_time?: string;
    end_time?: string;
  }) {
    return this.request(api.analyzeJointMovement, {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  static async clusterRoutes(params: {
    start_time: string;
    end_time: string;
    top_n?: number;
    min_vehicles_per_route?: number;
  }) {
    return this.request(api.clusterRoutes, {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  static async getVehicleTrack(vehicleId: string, startTime?: string, endTime?: string) {
    const params = new URLSearchParams();
    if (startTime) params.append('start_time', startTime);
    if (endTime) params.append('end_time', endTime);
    const queryString = params.toString();
    return this.request(`${api.getVehicleTrack(vehicleId)}${queryString ? '?' + queryString : ''}`);
  }

  static async getDetectors() {
    return this.request(api.getDetectors);
  }

  static async buildRoadGraph(maxDistanceMeters?: number) {
    const params = maxDistanceMeters ? `?max_distance_meters=${maxDistanceMeters}` : '';
    return this.request(`${api.buildRoadGraph}${params}`, {
      method: 'POST',
    });
  }
}