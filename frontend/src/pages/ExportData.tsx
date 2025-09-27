// src/pages/ExportData.tsx - Updated version
import React, { useState } from 'react';
import { ApiService } from '../api/services'; // Adjust import path as needed

const ExportData: React.FC = () => {
  const [exportType, setExportType] = useState('public_fines');
  const [format, setFormat] = useState('csv');
  const [loading, setLoading] = useState(false);

  const handleExport = async () => {
    setLoading(true);
    try {
      const blob = await ApiService.exportData(exportType, format);
      
      // Trigger download
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${exportType}_export.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      alert('Export completed successfully!');
    } catch (error: any) {
      alert('Export failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-md mx-auto">
      <h1 className="text-2xl font-bold mb-6">Export Data</h1>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">Data Type:</label>
          <select 
            value={exportType} 
            onChange={(e) => setExportType(e.target.value)}
            className="border p-2 w-full rounded"
          >
            <option value="public_fines">Public Fines</option>
            <option value="accidents">Accidents Statistics</option>
            <option value="traffic_lights">Traffic Lights</option>
            <option value="evacuations">Evacuations</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-2">Format:</label>
          <select 
            value={format} 
            onChange={(e) => setFormat(e.target.value)}
            className="border p-2 w-full rounded"
          >
            <option value="csv">CSV</option>
            <option value="excel">Excel</option>
          </select>
        </div>
        
        <button 
          onClick={handleExport}
          disabled={loading}
          className="bg-green-500 text-white px-6 py-2 rounded disabled:opacity-50 hover:bg-green-600 w-full"
        >
          {loading ? 'Exporting...' : 'Export Data'}
        </button>
      </div>
    </div>
  );
};

export default ExportData;