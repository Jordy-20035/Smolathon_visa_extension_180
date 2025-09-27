import React, { useEffect, useState } from 'react';
import { ApiService } from '../api/services';
import { DashboardAnalytics } from '../types';

const Dashboard: React.FC = () => {
  const [analytics, setAnalytics] = useState<DashboardAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [userRole, setUserRole] = useState<string>('citizen');

  useEffect(() => {
    // Get user role from localStorage
    const userData = localStorage.getItem('user');
    if (userData) {
      try {
        const user = JSON.parse(userData);
        setUserRole(user.role);
      } catch (e) {
        console.error('Error parsing user data:', e);
      }
    }

    const loadDashboard = async () => {
      try {
        console.log('Loading dashboard for role:', userRole);
        
        let dashboardData: DashboardAnalytics;
        
        if (userRole === 'admin' || userRole === 'redactor') {
          // Load full dashboard for admin/redactor
          dashboardData = await ApiService.getDashboardAnalytics();
        } else {
          // Load public dashboard for citizens
          dashboardData = await ApiService.getPublicDashboardAnalytics();
        }
        
        console.log('Dashboard data loaded:', dashboardData);
        setAnalytics(dashboardData);
      } catch (error) {
        console.error('Failed to load dashboard:', error);
        const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
        setError(`Failed to load dashboard data: ${errorMessage}`);
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, [userRole]);

  // Safe data access functions
  const getFinesCount = () => analytics?.fines?.total_count || 0;
  const getFinesAmount = () => analytics?.fines?.total_amount || 0;
  const getAccidentsCount = () => analytics?.accidents?.total_count || 0;
  const getTrafficLightsCount = () => analytics?.traffic_lights?.total_count || 0;

  // Role-based content rendering
  const renderPublicData = () => (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Public Traffic Statistics</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-4 rounded shadow border">
          <h3 className="font-semibold text-lg mb-2">Traffic Incidents</h3>
          <p className="text-2xl font-bold text-blue-600">{getAccidentsCount()}</p>
          <p className="text-sm text-gray-600">Reported incidents</p>
        </div>
        
        <div className="bg-white p-4 rounded shadow border">
          <h3 className="font-semibold text-lg mb-2">Traffic Lights</h3>
          <p className="text-2xl font-bold text-green-600">{getTrafficLightsCount()}</p>
          <p className="text-sm text-gray-600">Active signals</p>
        </div>
      </div>
      <p className="mt-4 text-gray-600 text-sm">
        Note: Financial data and detailed analytics are available to authorized personnel only.
      </p>
    </div>
  );

  const renderAdminData = () => (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">
        {userRole === 'admin' ? 'Administrative Dashboard' : 'Editor Dashboard'}
      </h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-4 rounded shadow border">
          <h3 className="font-semibold text-lg mb-2">Fines</h3>
          <p className="text-2xl font-bold text-blue-600">{getFinesCount()}</p>
          <p className="text-sm text-gray-600">
            Total amount: ${getFinesAmount().toLocaleString()}
          </p>
        </div>
        
        <div className="bg-white p-4 rounded shadow border">
          <h3 className="font-semibold text-lg mb-2">Accidents</h3>
          <p className="text-2xl font-bold text-red-600">{getAccidentsCount()}</p>
          <p className="text-sm text-gray-600">Last 30 days</p>
        </div>
        
        <div className="bg-white p-4 rounded shadow border">
          <h3 className="font-semibold text-lg mb-2">Traffic Lights</h3>
          <p className="text-2xl font-bold text-green-600">{getTrafficLightsCount()}</p>
          <p className="text-sm text-gray-600">Total installed</p>
        </div>
      </div>
    </div>
  );

  if (loading) return <div className="flex justify-center items-center h-64">Loading dashboard...</div>;
  if (error) return <div className="text-red-500 p-4">Error: {error}</div>;

  return userRole === 'admin' || userRole === 'redactor' ? renderAdminData() : renderPublicData();
};

export default Dashboard;