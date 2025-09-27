// src/pages/ImportData.tsx - Updated version
import React, { useState, useEffect } from 'react';
import { ApiService } from '../api/services'; // Adjust import path as needed

const ImportData: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [modelType, setModelType] = useState('fines');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [columnMappings, setColumnMappings] = useState<any>({});
  const [availableMappings, setAvailableMappings] = useState<any>({});

  // Load available column mappings when model type changes
  useEffect(() => {
    const loadMappings = async () => {
      try {
        const data = await ApiService.getColumnMappings(modelType);
        setAvailableMappings(data.available_mappings || {});
        
        // Set default mapping
        setColumnMappings(data.available_mappings || {});
      } catch (error) {
        console.error('Failed to load mappings:', error);
        // Fallback to default mappings if API fails
        const defaultMappings = {
          fines: {
            "Дата нарушения": "issued_at",
            "Госномер": "plate_number", 
            "Код нарушения": "violation_code",
            "Сумма штрафа": "amount",
            "Адрес": "address",
            "Статус": "status"
          },
          accidents: {
            "Тип ДТП": "accident_type",
            "Тяжесть": "severity", 
            "Пострадавшие": "casualties",
            "Дата и время": "occurred_at",
            "Адрес": "address"
          },
          traffic_lights: {
            "Тип светофора": "type",
            "Статус": "status",
            "Дата установки": "install_date", 
            "Адрес": "address"
          }
        };
        
        setAvailableMappings(defaultMappings[modelType as keyof typeof defaultMappings] || {});
        setColumnMappings(defaultMappings[modelType as keyof typeof defaultMappings] || {});
      }
    };
    
    loadMappings();
  }, [modelType]);

  const handleImport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      alert('Please select a file');
      return;
    }

    setLoading(true);
    try {
      const importResult = await ApiService.importData(modelType, file, columnMappings);
      setResult(importResult);
      alert(`Import successful! Processed: ${importResult.total_processed}, Successful: ${importResult.successful}`);
    } catch (error: any) {
      alert('Import failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleMappingChange = (fileColumn: string, dbColumn: string) => {
    setColumnMappings((prev: any) => ({
      ...prev,
      [fileColumn]: dbColumn
    }));
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Import Data</h1>
      
      <form onSubmit={handleImport} className="space-y-6">
        {/* Model Type Selection */}
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
        
        {/* File Upload */}
        <div>
          <label className="block text-sm font-medium mb-2">Upload File:</label>
          <input 
            type="file" 
            accept=".csv,.xlsx,.xls"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="border p-2 w-full rounded"
          />
          <p className="text-sm text-gray-600 mt-1">Supported formats: CSV, Excel (.xlsx, .xls)</p>
        </div>

        {/* Column Mapping Editor - Only show if we have mappings */}
        {Object.keys(availableMappings).length > 0 && (
          <div className="border rounded p-4">
            <h3 className="font-semibold mb-3">Column Mapping</h3>
            <p className="text-sm text-gray-600 mb-3">Map your file columns to database fields:</p>
            
            {Object.entries(availableMappings).map(([fileCol, dbCol]) => (
              <div key={fileCol} className="flex items-center gap-4 mb-2">
                <span className="w-48 font-medium">{fileCol}</span>
                <span className="text-gray-400">→</span>
                <input 
                  type="text"
                  value={columnMappings[fileCol] || ''}
                  onChange={(e) => handleMappingChange(fileCol, e.target.value)}
                  placeholder={dbCol as string}
                  className="border p-1 flex-1 rounded"
                />
              </div>
            ))}
          </div>
        )}
        
        <button 
          type="submit" 
          disabled={loading || !file}
          className="bg-blue-500 text-white px-6 py-2 rounded disabled:opacity-50 hover:bg-blue-600"
        >
          {loading ? 'Importing...' : 'Import Data'}
        </button>
      </form>

      {/* Results Display */}
      {result && (
        <div className="mt-6 p-4 bg-gray-100 rounded">
          <h3 className="font-semibold mb-2">Import Results:</h3>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>Total Processed: <strong>{result.total_processed}</strong></div>
            <div>Successful: <strong className="text-green-600">{result.successful}</strong></div>
            <div>Failed: <strong className="text-red-600">{result.failed}</strong></div>
          </div>
          
          {result.errors && result.errors.length > 0 && (
            <div className="mt-3">
              <h4 className="font-medium text-red-600">Errors:</h4>
              <ul className="text-sm text-red-600 list-disc list-inside">
                {result.errors.map((error: string, index: number) => (
                  <li key={index}>{error}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ImportData;