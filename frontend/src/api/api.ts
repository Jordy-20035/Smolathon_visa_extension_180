const API_BASE_URL = 'http://localhost:8000';

export const api = {
  // Authentication
  login: `${API_BASE_URL}/auth/login`,
  getCurrentUser: `${API_BASE_URL}/auth/me`,
  
  // Data endpoints
  getFines: `${API_BASE_URL}/data/fines`,
  getAccidents: `${API_BASE_URL}/data/accidents`,
  getTrafficLights: `${API_BASE_URL}/data/traffic-lights`,
  
  // Analytics
  getFinesAnalytics: `${API_BASE_URL}/analytics/fines`,
  getAccidentsAnalytics: `${API_BASE_URL}/analytics/accidents`,
  getTrafficLightsAnalytics: `${API_BASE_URL}/analytics/traffic-lights`,
  getDashboardAnalytics: `${API_BASE_URL}/analytics/dashboard`,
  getPublicDashboardAnalytics: `${API_BASE_URL}/analytics/public/dashboard`,
  getEvacuationsAnalytics: `${API_BASE_URL}/analytics/evacuations`, // This line is crucial


  // Content
  getContentPages: `${API_BASE_URL}/content/pages`,
  getNews: `${API_BASE_URL}/content/news`,

  // Import/Export - FIXED: Use consistent endpoints
  importData: (modelType: string) => `${API_BASE_URL}/api/v1/import/${modelType}`,
  getColumnMappings: (modelType: string) => `${API_BASE_URL}/api/v1/import/mappings/${modelType}`,
  exportData: (exportType: string) => `${API_BASE_URL}/api/v1/export/${exportType}`,
  
  // Specific endpoints
  exportEvacuations: `${API_BASE_URL}/api/v1/evacuations/export`,
  downloadTemplate: `${API_BASE_URL}/api/v1/evacuations/template`,
};