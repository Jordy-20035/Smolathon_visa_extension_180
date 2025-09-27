// src/pages/ImportData.tsx
import React, { useState } from 'react';
import { ApiService } from '../api/services';

const ImportData: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [modelType, setModelType] = useState('fines');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleImport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    try {
      const importResult = await ApiService.importData(modelType, file, {});
      setResult(importResult);
      alert('Data imported successfully!');
    } catch (error: any) { // Fix: Add type annotation
      alert('Import failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Import Data</h1>
      
      <form onSubmit={handleImport} className="max-w-md">
        <div className="mb-4">
          <label className="block mb-2">Data Type:</label>
          <select 
            value={modelType} 
            onChange={(e) => setModelType(e.target.value)}
            className="border p-2 w-full"
          >
            <option value="fines">Fines</option>
            <option value="accidents">Accidents</option>
            <option value="traffic_lights">Traffic Lights</option>
          </select>
        </div>
        
        <div className="mb-4">
          <label className="block mb-2">CSV File:</label>
          <input 
            type="file" 
            accept=".csv,.xlsx,.xls"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="border p-2 w-full"
          />
        </div>
        
        <button 
          type="submit" 
          disabled={loading || !file}
          className="bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50"
        >
          {loading ? 'Importing...' : 'Import Data'}
        </button>
      </form>

      {result && (
        <div className="mt-4 p-4 bg-gray-100 rounded">
          <h3 className="font-semibold">Import Result:</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default ImportData;