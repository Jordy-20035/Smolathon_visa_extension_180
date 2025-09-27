import React, { useState, useEffect } from 'react';
import { ApiService } from '../api/services';
import { useNavigate } from 'react-router-dom';


const Admin: React.FC = () => {
  const [user, setUser] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'import' | 'export' | 'content'>('import');
  const [file, setFile] = useState<File | null>(null);
  const [modelType, setModelType] = useState('fines');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const navigate = useNavigate();

  // Check authentication on component mount
  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      const userObj = JSON.parse(userData);
      setUser(userObj);
      
      // Redirect if not admin or redactor
      if (userObj.role !== 'admin' && userObj.role !== 'redactor') {
        navigate('/dashboard');
      }
    } else {
      navigate('/login');
    }
  }, [navigate]);

  const handleImport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    try {
      const columnMapping = {
        "issued_at": "Дата нарушения",
        "plate_number": "Номер автомобиля", 
        "violation_code": "Код нарушения",
        "amount": "Сумма штрафа"
      };
      
      const importResult = await ApiService.importData(modelType, file, columnMapping);
      setResult(importResult);
      alert('Data imported successfully!');
    } catch (error: any) {
      console.error('Import error:', error);
      alert('Import failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Show loading while checking auth
  if (!user) {
    return <div className="flex justify-center items-center h-64">Loading...</div>;
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-2">Admin Panel</h1>
      <p className="text-gray-600 mb-6">Welcome, {user.username} ({user.role})</p>
      
      {/* Tab Navigation */}
      <div className="flex border-b mb-6">
        <button
          className={`px-4 py-2 font-medium ${
            activeTab === 'import' 
              ? 'border-b-2 border-blue-500 text-blue-600' 
              : 'text-gray-500'
          }`}
          onClick={() => setActiveTab('import')}
        >
          Import Data
        </button>
        <button
          className={`px-4 py-2 font-medium ${
            activeTab === 'export' 
              ? 'border-b-2 border-blue-500 text-blue-600' 
              : 'text-gray-500'
          }`}
          onClick={() => setActiveTab('export')}
        >
          Export Data
        </button>
        <button
          className={`px-4 py-2 font-medium ${
            activeTab === 'content' 
              ? 'border-b-2 border-blue-500 text-blue-600' 
              : 'text-gray-500'
          }`}
          onClick={() => setActiveTab('content')}
        >
          Content Management
        </button>
      </div>

      {/* Import Tab */}
      {activeTab === 'import' && (
        <div>
          <h2 className="text-xl font-bold mb-4">Import Data</h2>
          <form onSubmit={handleImport} className="max-w-md space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Data Type:</label>
              <select 
                value={modelType} 
                onChange={(e) => setModelType(e.target.value)}
                className="border p-2 w-full rounded"
              >
                <option value="fines">Fines</option>
                <option value="accidents">Accidents</option>
                <option value="traffic_lights">Traffic Lights</option>
                <option value="evacuations">Evacuations</option>
              
              </select>
              
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">File (CSV or Excel):</label>
              <input 
                type="file" 
                accept=".csv,.xlsx,.xls"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="border p-2 w-full rounded"
              />
              <p className="text-sm text-gray-600 mt-1">
                Supported formats: CSV, XLSX, XLS
              </p>
            </div>
            
            <div className="bg-yellow-50 p-3 rounded">
              <p className="text-sm text-yellow-800">
                <strong>Note:</strong> For files with Russian headers, the system will automatically map:
                <br/>- "Дата нарушения" → Issue Date
                <br/>- "Номер автомобиля" → Plate Number
                <br/>- "Код нарушения" → Violation Code
                <br/>- "Сумма штрафа" → Amount
              </p>
            </div>
            
            <button 
              type="submit" 
              disabled={loading || !file}
              className="bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50 hover:bg-blue-600 transition"
            >
              {loading ? 'Importing...' : 'Import Data'}
            </button>
          </form>

          {result && (
            <div className="mt-6 p-4 bg-gray-100 rounded">
              <h3 className="font-semibold mb-2">Import Result:</h3>
              <pre className="text-sm">{JSON.stringify(result, null, 2)}</pre>
            </div>
          )}
        </div>
      )}

      {/* Export Tab */}
      {activeTab === 'export' && (
        <div>
          <h2 className="text-xl font-bold mb-4">Export Data</h2>
          <p className="text-gray-600">Export functionality coming soon...</p>
        </div>
      )}

      {/* Content Management Tab */}
      {activeTab === 'content' && (
        <div>
          <h2 className="text-xl font-bold mb-4">Content Management</h2>
          <p className="text-gray-600">Content management functionality coming soon...</p>
        </div>
      )}
    </div>
  );
};

export default Admin;