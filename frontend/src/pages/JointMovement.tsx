import React, { useState, useEffect } from 'react';
import { ApiService } from '../api/services';
import TrafficMap from '../components/map/TrafficMap';

interface JointMovementMatch {
  detector_id: string;
  detector_external_id: string;
  target_timestamp: string;
  other_timestamp: string;
  time_diff_seconds: number;
  latitude: number;
  longitude: number;
}

interface JointMovement {
  vehicle_id: string;
  common_nodes_count: number;
  matches: JointMovementMatch[];
  start_time: string;
  end_time: string;
  duration_seconds: number;
}

interface JointMovementResponse {
  target_vehicle_id: string;
  target_track: Array<{
    detector_id: string;
    detector_external_id: string;
    latitude: number;
    longitude: number;
    timestamp: string;
    speed?: number;
  }>;
  joint_movements: JointMovement[];
}

const JointMovement: React.FC = () => {
  const [vehicleId, setVehicleId] = useState<string>('');
  const [minCommonNodes, setMinCommonNodes] = useState<number>(3);
  const [maxTimeGap, setMaxTimeGap] = useState<number>(300);
  const [maxLead, setMaxLead] = useState<number>(60);
  const [startTime, setStartTime] = useState<string>('');
  const [endTime, setEndTime] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [data, setData] = useState<JointMovementResponse | null>(null);
  const [error, setError] = useState<string>('');
  const [selectedMovement, setSelectedMovement] = useState<JointMovement | null>(null);

  const handleAnalyze = async () => {
    if (!vehicleId.trim()) {
      setError('Введите идентификатор транспортного средства');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const result = await ApiService.analyzeJointMovement({
        target_vehicle_id: vehicleId,
        min_common_nodes: minCommonNodes,
        max_time_gap_seconds: maxTimeGap,
        max_lead_seconds: maxLead,
        start_time: startTime || undefined,
        end_time: endTime || undefined,
      });
      
      setData(result as JointMovementResponse);
    } catch (err: any) {
      setError(err.message || 'Ошибка при анализе совместного движения');
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  // Prepare map data
  const targetTrack = data?.target_track || [];
  const jointMovementTracks = data?.joint_movements.map(movement => ({
    vehicle_id: movement.vehicle_id,
    matches: movement.matches.map(match => ({
      latitude: match.latitude,
      longitude: match.longitude,
      detector_id: match.detector_external_id,
    })),
  })) || [];

  const detectors = [
    ...targetTrack.map(t => ({ latitude: t.latitude, longitude: t.longitude, detector_id: t.detector_external_id })),
    ...jointMovementTracks.flatMap(t => t.matches.map(m => ({ latitude: m.latitude, longitude: m.longitude, detector_id: m.detector_id }))),
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">Анализ совместного движения</h1>
      
      {/* Parameters Form */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Параметры анализа</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Идентификатор ТС *
            </label>
            <input
              type="text"
              value={vehicleId}
              onChange={(e) => setVehicleId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="Введите ID транспортного средства"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Минимум совпадающих узлов (K)
            </label>
            <input
              type="number"
              value={minCommonNodes}
              onChange={(e) => setMinCommonNodes(parseInt(e.target.value) || 3)}
              min={2}
              max={20}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Макс. временной разрыв (сек)
            </label>
            <input
              type="number"
              value={maxTimeGap}
              onChange={(e) => setMaxTimeGap(parseInt(e.target.value) || 300)}
              min={10}
              max={3600}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Макс. опережение (сек)
            </label>
            <input
              type="number"
              value={maxLead}
              onChange={(e) => setMaxLead(parseInt(e.target.value) || 60)}
              min={5}
              max={300}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Начало периода (опционально)
            </label>
            <input
              type="datetime-local"
              value={startTime}
              onChange={(e) => setStartTime(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Конец периода (опционально)
            </label>
            <input
              type="datetime-local"
              value={endTime}
              onChange={(e) => setEndTime(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
        </div>
        
        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
        >
          {loading ? 'Анализ...' : 'Анализировать'}
        </button>
        
        {error && (
          <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}
      </div>
      
      {/* Results */}
      {data && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Map */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">Визуализация</h2>
              <TrafficMap
                targetTrack={targetTrack}
                jointMovementTracks={jointMovementTracks}
                detectors={detectors}
                height="600px"
              />
            </div>
          </div>
          
          {/* Results List */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">
              Совместные движения ({data.joint_movements.length})
            </h2>
            
            {data.joint_movements.length === 0 ? (
              <p className="text-gray-500">Совместных движений не найдено</p>
            ) : (
              <div className="space-y-3 max-h-[600px] overflow-y-auto">
                {data.joint_movements.map((movement, idx) => (
                  <div
                    key={idx}
                    onClick={() => setSelectedMovement(movement)}
                    className={`p-4 border rounded-lg cursor-pointer transition ${
                      selectedMovement?.vehicle_id === movement.vehicle_id
                        ? 'border-green-500 bg-green-50'
                        : 'border-gray-200 hover:border-green-300'
                    }`}
                  >
                    <div className="font-semibold text-gray-800">
                      ТС: {movement.vehicle_id}
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      Совпадающих узлов: {movement.common_nodes_count}
                    </div>
                    <div className="text-sm text-gray-600">
                      Длительность: {Math.round(movement.duration_seconds)} сек
                    </div>
                    <div className="text-xs text-gray-500 mt-2">
                      {new Date(movement.start_time).toLocaleString('ru-RU')} - {new Date(movement.end_time).toLocaleString('ru-RU')}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Details */}
      {selectedMovement && (
        <div className="mt-6 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">
            Детали: ТС {selectedMovement.vehicle_id}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <strong>Количество совпадающих узлов:</strong> {selectedMovement.common_nodes_count}
            </div>
            <div>
              <strong>Длительность:</strong> {Math.round(selectedMovement.duration_seconds)} секунд
            </div>
            <div>
              <strong>Начало:</strong> {new Date(selectedMovement.start_time).toLocaleString('ru-RU')}
            </div>
            <div>
              <strong>Конец:</strong> {new Date(selectedMovement.end_time).toLocaleString('ru-RU')}
            </div>
          </div>
          
          <div className="mt-4">
            <strong>Детекторы с совпадениями:</strong>
            <div className="mt-2 space-y-2">
              {selectedMovement.matches.map((match, idx) => (
                <div key={idx} className="p-2 bg-gray-50 rounded">
                  <div><strong>Детектор:</strong> {match.detector_external_id}</div>
                  <div className="text-sm text-gray-600">
                    Разница времени: {match.time_diff_seconds.toFixed(2)} сек
                  </div>
                  <div className="text-xs text-gray-500">
                    Целевое ТС: {new Date(match.target_timestamp).toLocaleTimeString('ru-RU')} | 
                    Сопутствующее ТС: {new Date(match.other_timestamp).toLocaleTimeString('ru-RU')}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default JointMovement;
