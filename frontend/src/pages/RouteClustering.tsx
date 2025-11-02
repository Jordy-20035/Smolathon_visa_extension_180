import React, { useState } from 'react';
import { ApiService } from '../api/services';
import TrafficMap from '../components/map/TrafficMap';

interface Route {
  route_signature: string;
  detector_sequence: string[];
  total_vehicles: number;
  intensity_per_hour: number;
  average_speed_kmh: number | null;
  average_passage_time_seconds: number | null;
  coordinates: Array<{
    latitude: number;
    longitude: number;
    detector_id: string;
  }>;
  vehicles: string[];
}

interface RouteClusteringResponse {
  routes: Route[];
  time_range_hours: number;
  total_vehicles_analyzed: number;
}

const RouteClustering: React.FC = () => {
  const [startTime, setStartTime] = useState<string>('');
  const [endTime, setEndTime] = useState<string>('');
  const [topN, setTopN] = useState<number>(10);
  const [minVehicles, setMinVehicles] = useState<number>(2);
  const [loading, setLoading] = useState<boolean>(false);
  const [data, setData] = useState<RouteClusteringResponse | null>(null);
  const [error, setError] = useState<string>('');
  const [selectedRoute, setSelectedRoute] = useState<Route | null>(null);

  // Set default time range (last 2 hours)
  React.useEffect(() => {
    const now = new Date();
    const twoHoursAgo = new Date(now.getTime() - 2 * 60 * 60 * 1000);
    
    const formatDateTime = (date: Date) => {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      return `${year}-${month}-${day}T${hours}:${minutes}`;
    };
    
    if (!startTime) setStartTime(formatDateTime(twoHoursAgo));
    if (!endTime) setEndTime(formatDateTime(now));
  }, []);

  const handleAnalyze = async () => {
    if (!startTime || !endTime) {
      setError('Укажите временной диапазон');
      return;
    }

    if (new Date(startTime) >= new Date(endTime)) {
      setError('Время начала должно быть раньше времени окончания');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const result = await ApiService.clusterRoutes({
        start_time: new Date(startTime).toISOString(),
        end_time: new Date(endTime).toISOString(),
        top_n: topN,
        min_vehicles_per_route: minVehicles,
      });
      
      setData(result as RouteClusteringResponse);
    } catch (err: any) {
      setError(err.message || 'Ошибка при кластеризации маршрутов');
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  // Extract unique detectors from all routes
  const detectors = data?.routes.flatMap(route => 
    route.coordinates.map(coord => ({
      latitude: coord.latitude,
      longitude: coord.longitude,
      detector_id: coord.detector_id,
    }))
  ).filter((det, idx, self) => 
    idx === self.findIndex(d => d.detector_id === det.detector_id)
  ) || [];

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">Кластеризация маршрутов и анализ загруженности</h1>
      
      {/* Parameters Form */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Параметры анализа</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Начало периода *
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
              Конец периода *
            </label>
            <input
              type="datetime-local"
              value={endTime}
              onChange={(e) => setEndTime(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Топ-N маршрутов
            </label>
            <input
              type="number"
              value={topN}
              onChange={(e) => setTopN(parseInt(e.target.value) || 10)}
              min={1}
              max={50}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Мин. ТС на маршрут
            </label>
            <input
              type="number"
              value={minVehicles}
              onChange={(e) => setMinVehicles(parseInt(e.target.value) || 2)}
              min={1}
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
              <h2 className="text-xl font-semibold mb-4">Визуализация маршрутов</h2>
              <TrafficMap
                routes={data.routes}
                selectedRoute={selectedRoute}
                detectors={detectors}
                height="600px"
              />
            </div>
          </div>
          
          {/* Statistics */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">
              Топ-{data.routes.length} маршрутов
            </h2>
            
            <div className="mb-4 p-3 bg-blue-50 rounded">
              <div className="text-sm text-gray-700">
                <strong>Всего ТС проанализировано:</strong> {data.total_vehicles_analyzed}
              </div>
              <div className="text-sm text-gray-700">
                <strong>Временной диапазон:</strong> {data.time_range_hours.toFixed(2)} часов
              </div>
            </div>
            
            {data.routes.length === 0 ? (
              <p className="text-gray-500">Маршруты не найдены</p>
            ) : (
              <div className="space-y-3 max-h-[500px] overflow-y-auto">
                {data.routes.map((route, idx) => (
                  <div
                    key={idx}
                    onClick={() => setSelectedRoute(route)}
                    className={`p-4 border rounded-lg cursor-pointer transition ${
                      selectedRoute?.route_signature === route.route_signature
                        ? 'border-green-500 bg-green-50'
                        : 'border-gray-200 hover:border-green-300'
                    }`}
                  >
                    <div className="font-semibold text-gray-800">
                      Маршрут #{idx + 1}
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      <strong>Интенсивность:</strong> {route.intensity_per_hour.toFixed(2)} ТС/час
                    </div>
                    <div className="text-sm text-gray-600">
                      <strong>ТС:</strong> {route.total_vehicles}
                    </div>
                    {route.average_speed_kmh && (
                      <div className="text-sm text-gray-600">
                        <strong>Средняя скорость:</strong> {route.average_speed_kmh.toFixed(1)} км/ч
                      </div>
                    )}
                    {route.average_passage_time_seconds && (
                      <div className="text-sm text-gray-600">
                        <strong>Время прохождения:</strong> {Math.round(route.average_passage_time_seconds)} сек
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Route Details */}
      {selectedRoute && (
        <div className="mt-6 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">
            Детали маршрута #{data?.routes.indexOf(selectedRoute)! + 1}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <strong>Последовательность детекторов:</strong>
              <div className="mt-2 text-sm text-gray-700">
                {selectedRoute.detector_sequence.join(' → ')}
              </div>
            </div>
            <div>
              <strong>Общее количество ТС:</strong> {selectedRoute.total_vehicles}
            </div>
            <div>
              <strong>Интенсивность:</strong> {selectedRoute.intensity_per_hour.toFixed(2)} ТС/час
            </div>
            {selectedRoute.average_speed_kmh && (
              <div>
                <strong>Средняя скорость:</strong> {selectedRoute.average_speed_kmh.toFixed(2)} км/ч
              </div>
            )}
            {selectedRoute.average_passage_time_seconds && (
              <div>
                <strong>Среднее время прохождения:</strong> {Math.round(selectedRoute.average_passage_time_seconds)} секунд
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default RouteClustering;
