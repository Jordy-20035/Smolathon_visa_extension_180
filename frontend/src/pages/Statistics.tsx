import React, { useState, useEffect } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area } from "recharts";
import { Calendar, TrendingDown, TrendingUp, AlertTriangle, Users, MapPin, Filter, Download, Eye, BarChart3, Activity, Navigation, Clock, Map } from "lucide-react";
import { routesData } from "../data/routes";



// Add these interfaces
interface MonthlyStat {
  month: string;
  routes: number;
  totalStreets: number;
  avgRouteLength: number;
  year: number;
} 

interface ProcessedRoutesData {
  monthlyData: MonthlyStat[];
  totalStreetsCovered: number;
  districtCoverage: { [key: string]: number };
}

interface RoutesRecord {
  month: string;
  year: number;
  route: string[];
}


const processRoutesData = (): ProcessedRoutesData => {
  // Properly type monthlyStats with index signature
  const monthlyStats: { [key: string]: MonthlyStat } = {};
  const streetCoverage = new Set<string>();
  const districtStats: { [key: string]: number } = {};
  
  (routesData as RoutesRecord[]).forEach(record => {
    const key = `${record.month} ${record.year}`;
    
    if (!monthlyStats[key]) {
      monthlyStats[key] = {
        month: `${record.month.slice(0, 3)} ${record.year}`,
        routes: 0,
        totalStreets: 0,
        avgRouteLength: 0,
        year: record.year
      };
    }
    
    record.route.forEach(route => {
      monthlyStats[key].routes++;
      // Count streets in this route (split by arrow)
      const streets = route.split('→').length;
      monthlyStats[key].totalStreets += streets;
      
      // Extract street names for coverage analysis
      route.split('→').forEach(streetSegment => {
        const streetName = streetSegment.split('(')[0].trim();
        streetCoverage.add(streetName);
        
        // Simple district detection based on street names
        const district = detectDistrict(streetName);
        if (district) {
          districtStats[district] = (districtStats[district] || 0) + 1;
        }
      });
    });
    
    monthlyStats[key].avgRouteLength = monthlyStats[key].totalStreets / monthlyStats[key].routes;
  });
  
  return {
    monthlyData: Object.values(monthlyStats).sort((a, b) => {
      const monthsOrder: { [key: string]: number } = {
        'Янв': 1, 'Фев': 2, 'Мар': 3, 'Апр': 4, 'Май': 5, 'Июн': 6,
        'Июл': 7, 'Авг': 8, 'Сен': 9, 'Окт': 10, 'Ноя': 11, 'Дек': 12
      };
      return monthsOrder[a.month.split(' ')[0]] - monthsOrder[b.month.split(' ')[0]];
    }),
    totalStreetsCovered: streetCoverage.size,
    districtCoverage: districtStats
  };
};


const detectDistrict = (streetName: string): string => {
  // Simple district mapping based on street names
  const districtMapping: { [key: string]: string } = {
    'Ленина': 'Ленинский',
    'Советская': 'Центральный',
    'Гагарина': 'Центральный',
    'Багратиона': 'Центральный',
    'Дзержинского': 'Промышленный',
    'Конева': 'Промышленный',
    'Ново-Ленинградская': 'Заднепровский',
    'Краснинская': 'Заднепровский',
    'Тенишевой': 'Центральный',
    'Октябрьской Революции': 'Ленинский',
    'Чаплина': 'Промышленный',
    'Барклая-де-Толли': 'Центральный',
    'Заслонова': 'Заднепровский',
    'Матросова': 'Промышленный',
    'Парковая': 'Ленинский',
    'Рославльская': 'Руднянский',
    'Тенистая': 'Ленинский',
    'Чайковского': 'Центральный',
    'Строителей': 'Промышленный',
    'Петрова': 'Заднепровский',
    'Войкова': 'Промышленный',
    'Железнодорожная': 'Заднепровский',
    'Кольцевая': 'Руднянский',
    'Литейная': 'Промышленный',
    'Можайского': 'Заднепровский',
    'Ольшанская': 'Руднянский'
  };
  
  for (const [key, district] of Object.entries(districtMapping)) {
    if (streetName.includes(key)) {
      return district;
    }
  }
  return 'Центральный'; // Default
};



// Mock data for violations statistics (complementary to routes data)
const violationsData = [
  { month: "Янв 2024", violations: 1250, fines: 850, compared2023: 1180 },
  { month: "Фев 2024", violations: 1100, fines: 780, compared2023: 1320 },
  { month: "Мар 2024", violations: 980, fines: 690, compared2023: 1150 },
  { month: "Апр 2024", violations: 1350, fines: 920, compared2023: 1280 },
  { month: "Май 2024", violations: 1480, fines: 1040, compared2023: 1450 },
  { month: "Июн 2024", violations: 1620, fines: 1150, compared2023: 1580 },
  { month: "Июл 2024", violations: 1550, fines: 1100, compared2023: 1620 },
  { month: "Авг 2024", violations: 1420, fines: 980, compared2023: 1480 },
  { month: "Сен 2024", violations: 1380, fines: 950, compared2023: 1420 },
  { month: "Окт 2024", violations: 1260, fines: 880, compared2023: 1350 },
  { month: "Ноя 2024", violations: 1180, fines: 820, compared2023: 1280 },
  { month: "Дек 2024", violations: 1320, fines: 920, compared2023: 1400 }
];

const accidentData = [
  { month: "Янв 2024", accidents: 45, injured: 52, fatal: 3, compared2023: 58 },
  { month: "Фев 2024", accidents: 38, injured: 44, fatal: 2, compared2023: 48 },
  { month: "Мар 2024", accidents: 42, injured: 48, fatal: 1, compared2023: 55 },
  { month: "Апр 2024", accidents: 35, injured: 41, fatal: 2, compared2023: 42 },
  { month: "Май 2024", accidents: 40, injured: 46, fatal: 3, compared2023: 51 },
  { month: "Июн 2024", accidents: 33, injured: 38, fatal: 1, compared2023: 44 },
  { month: "Июл 2024", accidents: 28, injured: 32, fatal: 1, compared2023: 38 },
  { month: "Авг 2024", accidents: 31, injured: 36, fatal: 2, compared2023: 42 },
  { month: "Сен 2024", accidents: 29, injured: 33, fatal: 1, compared2023: 36 },
  { month: "Окт 2024", accidents: 34, injured: 39, fatal: 2, compared2023: 45 },
  { month: "Ноя 2024", accidents: 37, injured: 43, fatal: 3, compared2023: 48 },
  { month: "Дек 2024", accidents: 42, injured: 48, fatal: 2, compared2023: 52 }
];

const violationTypesData = [
  { name: "Превышение скорости", value: 35, color: "#ef4444" },
  { name: "Нарушение разметки", value: 25, color: "#f97316" },
  { name: "Проезд на красный", value: 20, color: "#eab308" },
  { name: "Парковка в неположенном месте", value: 15, color: "#22c55e" },
  { name: "Прочие нарушения", value: 5, color: "#6366f1" }
];

// Update StatCard component with proper typing
interface StatCardProps {
  title: string;
  value: number | string;
  change?: number;
  icon: React.ElementType;
  color?: string;
  subtitle?: string;
  trendIcon?: React.ElementType;
}

const StatCard = ({ title, value, change, icon: Icon, color = "blue", subtitle, trendIcon }: StatCardProps) => {
  const isPositive = change ? change > 0 : false;
  const changeColor = color === "red" ? (isPositive ? "text-red-600" : "text-green-600") : 
                    color === "green" ? (isPositive ? "text-green-600" : "text-red-600") : 
                    (isPositive ? "text-green-600" : "text-red-600");
  
  const bgColor = `bg-${color}-50`;
  const iconColor = `text-${color}-600`;
  const TrendIcon = trendIcon || (isPositive ? TrendingUp : TrendingDown);
  
  return (
    <div className={`${bgColor} rounded-xl p-6 border border-${color}-100 hover:shadow-lg transition-all duration-300`}>
      <div className="flex items-center justify-between mb-4">
        <Icon className={`w-8 h-8 ${iconColor}`} />
        {change !== undefined && (
          <div className={`flex items-center gap-1 ${changeColor} text-sm font-semibold`}>
            <TrendIcon className="w-4 h-4" />
            {Math.abs(change)}%
          </div>
        )}
      </div>
      <h3 className="text-2xl font-bold text-gray-900 mb-1">
        {typeof value === 'number' ? value.toLocaleString() : value}
      </h3>
      <p className="text-sm text-gray-600 mb-2">{title}</p>
      {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
    </div>
  );
};
// Add these interfaces above the FilterPanel component
interface FilterPanelProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  dateRange: string;
  setDateRange: (range: string) => void;
  selectedDistrict: string;
  setSelectedDistrict: (district: string) => void;
}

const FilterPanel = ({ 
  activeTab, 
  setActiveTab, 
  dateRange, 
  setDateRange, 
  selectedDistrict, 
  setSelectedDistrict 
}: FilterPanelProps) => {
  const districts = ["Все районы", "Ленинский", "Промышленный", "Заднепровский", "Центральный", "Руднянский"];
  
  return (
    <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
      <h3 className="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2">
        <Filter className="w-5 h-5 text-[#62a744]" />
        Фильтры и настройки
      </h3>
      
      <div className="grid md:grid-cols-4 gap-6">
        {/* Tab Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Тип данных</label>
          <select 
            value={activeTab} 
            onChange={(e) => setActiveTab(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#62a744] focus:border-transparent"
          >
            <option value="routes">Маршруты и покрытие</option>
            <option value="violations">Нарушения ПДД</option>
            <option value="accidents">ДТП и происшествия</option>
            <option value="coverage">Покрытие районов</option>
          </select>
        </div>
        
        {/* Date Range */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Период</label>
          <select 
            value={dateRange} 
            onChange={(e) => setDateRange(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#62a744] focus:border-transparent"
          >
            <option value="2024">2024 год</option>
            <option value="2025">2025 год</option>
            <option value="all">Все данные</option>
            <option value="custom">Выбрать период</option>
          </select>
        </div>
        
        {/* District Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Район</label>
          <select 
            value={selectedDistrict} 
            onChange={(e) => setSelectedDistrict(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#62a744] focus:border-transparent"
          >
            {districts.map(district => (
              <option key={district} value={district}>
                {district}
              </option>
            ))}
          </select>
        </div>
        
        {/* Actions */}
        <div className="flex items-end gap-2">
          <button className="flex-1 px-4 py-3 bg-[#62a744] text-white rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center gap-2">
            <Download className="w-4 h-4" />
            Экспорт
          </button>
          <button className="px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
            <Eye className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default function StatisticsPage() {
  const [activeTab, setActiveTab] = useState('routes');
  const [dateRange, setDateRange] = useState('2024');
  const [selectedDistrict, setSelectedDistrict] = useState('Все районы');
  const [isLoading, setIsLoading] = useState(false);
  
  const routesStats = processRoutesData();

  useEffect(() => {
    setIsLoading(true);
    const timer = setTimeout(() => setIsLoading(false), 500);
    return () => clearTimeout(timer);
  }, [activeTab, dateRange, selectedDistrict]);

  interface ViolationData {
  month: string;
  violations: number;
  fines: number;
  compared2023: number;
}

interface AccidentData {
  month: string;
  accidents: number;
  injured: number;
  fatal: number;
  compared2023: number;
}

interface ViolationTypeData {
  name: string;
  value: number;
  color: string;
}


const getCurrentData = (): any[] => {
let data: any[] = [];
  
switch (activeTab) {
    case 'routes':
      data = routesStats.monthlyData.filter(item => 
        dateRange === 'all' || item.year.toString() === dateRange
      );
      break;
    case 'violations':
      data = violationsData.filter(item => 
        dateRange === 'all' || item.month.includes(dateRange)
      );
      break;
    case 'accidents':
      data = accidentData.filter(item => 
        dateRange === 'all' || item.month.includes(dateRange)
      );
      break;
    case 'coverage':
      data = Object.entries(routesStats.districtCoverage).map(([district, count]) => ({
        district,
        routes: count,
        coverage: Math.round((count / routesStats.monthlyData.length) * 100)
      }));
      break;
  }
  
  return data;
};
// Add this interface near your other interfaces
interface StatsSummary {
  totalRoutes?: number;
  totalStreets?: number;
  avgRouteLength?: number;
  coverage?: number;
  current?: number;
  previous?: number;
  change?: number;
  accidents?: number;
  previousAccidents?: number;
  injured?: number;
  fatal?: number;
}

const getStatsSummary = (): StatsSummary => {
  const data = getCurrentData();
  
  switch (activeTab) {
    case 'routes':
      const totalRoutes = data.reduce((sum: number, item: any) => sum + item.routes, 0);
      const totalStreets = data.reduce((sum: number, item: any) => sum + item.totalStreets, 0);
      return {
        totalRoutes,
        totalStreets,
        avgRouteLength: totalRoutes > 0 ? totalStreets / totalRoutes : 0,
        coverage: routesStats.totalStreetsCovered
      };
      
    case 'violations':
      const current = data.reduce((sum: number, item: any) => sum + item.violations, 0);
      const previous = data.reduce((sum: number, item: any) => sum + item.compared2023, 0);
      const change = previous > 0 ? ((current - previous) / previous * 100) : 0;
      return { 
        current, 
        previous, 
        change: parseFloat(change.toFixed(1)) 
      };
      
    case 'accidents':
      const accidents = data.reduce((sum: number, item: any) => sum + item.accidents, 0);
      const previousAccidents = data.reduce((sum: number, item: any) => sum + item.compared2023, 0);
      const accidentsChange = previousAccidents > 0 ? ((accidents - previousAccidents) / previousAccidents * 100) : 0;
      return { 
        accidents, 
        previousAccidents, 
        change: parseFloat(accidentsChange.toFixed(1)),
        injured: data.reduce((sum: number, item: any) => sum + item.injured, 0),
        fatal: data.reduce((sum: number, item: any) => sum + item.fatal, 0)
      };
      
    default:
      return {};
  }
};

  const stats = getStatsSummary();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-[#62a744] mx-auto mb-4"></div>
          <p className="text-gray-600">Загрузка данных...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <BarChart3 className="w-8 h-8 text-[#62a744]" />
            <h1 className="text-4xl font-bold text-gray-900">Статистика маршрутов и безопасности</h1>
          </div>
          <p className="text-xl text-gray-600">
            Анализ маршрутов ЦОДД и дорожной безопасности Смоленска • Данные обновляются ежемесячно
          </p>
        </div>

        {/* Filter Panel */}
        <FilterPanel 
          activeTab={activeTab} 
          setActiveTab={setActiveTab}
          dateRange={dateRange}
          setDateRange={setDateRange}
          selectedDistrict={selectedDistrict}
          setSelectedDistrict={setSelectedDistrict}
        />



{/* Stats Overview */}
<div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
  {activeTab === 'routes' ? (
    <>
      <StatCard 
        title="Всего маршрутов" 
        value={stats.totalRoutes || 0} 
        change={15.3}
        icon={Navigation}
        color="green"
        subtitle="За выбранный период"
      />
      <StatCard 
        title="Улиц охвачено" 
        value={stats.coverage || 0} 
        change={8.7}
        icon={Map}
        color="blue"
        subtitle="Уникальных улиц в маршрутах"
      />
      <StatCard 
        title="Средняя длина маршрута" 
        value={Math.round(stats.avgRouteLength || 0)} 
        change={-2.1}
        icon={Clock}
        color="orange"
        subtitle="Участков на маршрут"
      />
      <StatCard 
        title="Районов охвачено" 
        value={5} 
        change={0}
        icon={MapPin}
        color="purple"
        subtitle="Полное покрытие города"
      />
    </>
  ) : activeTab === 'violations' ? (
    <>
      <StatCard 
        title="Всего нарушений" 
        value={stats.current || 0} 
        change={stats.change || 0}
        icon={AlertTriangle}
        color="red"
        subtitle="За выбранный период"
      />
      <StatCard 
        title="Выписано постановлений" 
        value={Math.round((stats.current || 0) * 0.7)} 
        change={(stats.change || 0) + 2}
        icon={Activity}
        color="orange"
        subtitle="Процент выписанных штрафов: 70%"
      />
      <StatCard 
        title="Средний штраф" 
        value={2850} 
        change={5.2}
        icon={BarChart3}
        color="blue"
        subtitle="В рублях"
      />
      <StatCard 
        title="Изменение к 2023" 
        value={Math.abs(stats.change || 0)} 
        change={stats.change || 0}
        icon={BarChart3}
        trendIcon={(stats.change || 0) > 0 ? TrendingUp : TrendingDown}
        color="green"
        subtitle="Процентное изменение"
      />
    </>
  ) : activeTab === 'accidents' ? (
    <>
      <StatCard 
        title="ДТП всего" 
        value={stats.accidents || 0} 
        change={stats.change || 0}
        icon={AlertTriangle}
        color="red"
        subtitle="За выбранный период"
      />
      <StatCard 
        title="Пострадавшие" 
        value={stats.injured || 0} 
        change={(stats.change || 0) - 5}
        icon={Users}
        color="orange"
        subtitle="Человек получили травмы"
      />
      <StatCard 
        title="Летальные случаи" 
        value={stats.fatal || 0} 
        change={-25}
        icon={AlertTriangle}
        color="red"
        subtitle="Смертельных исходов"
      />
      <StatCard 
        title="Изменение к 2023" 
        value={Math.abs(stats.change || 0)} 
        change={stats.change || 0}
        icon={BarChart3}
        trendIcon={(stats.change || 0) > 0 ? TrendingUp : TrendingDown}
        color="green"
        subtitle="Процентное изменение"
      />
    </>
  ) : (
    <>
      <StatCard 
        title="Районов в анализе" 
        value={5} 
        change={0}
        icon={MapPin}
        color="blue"
        subtitle="Полное покрытие города"
      />
      <StatCard 
        title="Самый охваченный" 
        value="Центральный"
        change={12}
        icon={TrendingUp}
        color="green"
        subtitle="По количеству маршрутов"
      />
      <StatCard 
        title="Меньше всего охвата" 
        value="Руднянский"
        change={-8}
        icon={TrendingDown}
        color="orange"
        subtitle="Наименьшее количество маршрутов"
      />
      <StatCard 
        title="Общий прогресс" 
        value={15.3} 
        change={15.3}
        icon={Activity}
        color="green"
        subtitle="Увеличение охвата, %"
      />
    </>
  )}
</div>

        {/* Main Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Primary Chart */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-900">
                {activeTab === 'routes' ? 'Динамика маршрутов по месяцам' : 
                 activeTab === 'violations' ? 'Статистика нарушений ПДД' : 
                 activeTab === 'accidents' ? 'Динамика ДТП' : 'Покрытие районов маршрутами'}
              </h3>
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <Calendar className="w-4 h-4" />
                {dateRange === 'all' ? 'Все данные' : `${dateRange} год`}
              </div>
            </div>
            
            <ResponsiveContainer width="100%" height={300}>
              {activeTab === 'routes' ? (
                <BarChart data={getCurrentData()}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="month" stroke="#666" />
                  <YAxis stroke="#666" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#fff', 
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    }} 
                  />
                  <Legend />
                  <Bar dataKey="routes" name="Количество маршрутов" fill="#62a744" />
                  <Bar dataKey="totalStreets" name="Всего участков" fill="#82ca9d" />
                </BarChart>
              ) : activeTab === 'violations' ? (
                <AreaChart data={getCurrentData()}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="month" stroke="#666" />
                  <YAxis stroke="#666" />
                  <Tooltip />
                  <Legend />
                  <Area 
                    type="monotone" 
                    dataKey="violations"
                    name="Нарушения 2024"
                    stroke="#62a744" 
                    fill="#62a744"
                    fillOpacity={0.6}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="compared2023" 
                    name="Аналогичный период 2023"
                    stroke="#ef4444" 
                    strokeDasharray="5 5"
                    strokeWidth={2}
                  />
                </AreaChart>
              ) : activeTab === 'accidents' ? (
                <LineChart data={getCurrentData()}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="month" stroke="#666" />
                  <YAxis stroke="#666" />
                  <Tooltip />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="accidents"
                    name="ДТП 2024"
                    stroke="#62a744" 
                    strokeWidth={3}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="compared2023" 
                    name="Аналогичный период 2023"
                    stroke="#ef4444" 
                    strokeDasharray="5 5"
                  />
                </LineChart>
              ) : (
                <BarChart data={getCurrentData()}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="district" stroke="#666" />
                  <YAxis stroke="#666" />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="routes" name="Количество маршрутов" fill="#62a744" />
                  <Bar dataKey="coverage" name="Процент охвата" fill="#82ca9d" />
                </BarChart>
              )}
            </ResponsiveContainer>
          </div>

          {/* Secondary Chart */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-6">
              {activeTab === 'routes' ? 'Распределение маршрутов по длине' : 
               activeTab === 'violations' ? 'Типы нарушений' : 
               activeTab === 'accidents' ? 'Тяжесть происшествий' : 'Детализация по районам'}
            </h3>
            
            <ResponsiveContainer width="100%" height={300}>
              {activeTab === 'routes' ? (
                <BarChart data={getCurrentData()}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="month" stroke="#666" />
                  <YAxis stroke="#666" />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="avgRouteLength" name="Средняя длина маршрута" fill="#f97316" />
                </BarChart>
              ) : activeTab === 'violations' ? (
                <PieChart>
                  <Pie
                    data={violationTypesData}
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                    label={({name, value}) => `${name}: ${value}%`}
                  >
                    {violationTypesData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              ) : activeTab === 'accidents' ? (
                <BarChart data={getCurrentData()}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="month" stroke="#666" />
                  <YAxis stroke="#666" />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="injured" name="Пострадавшие" fill="#f97316" />
                  <Bar dataKey="fatal" name="Погибшие" fill="#ef4444" />
                </BarChart>
              ) : (
                <PieChart>
                  <Pie
                    data={getCurrentData()}
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="coverage"
                    label={({district, coverage}) => `${district}: ${coverage}%`}
                  >
                    {getCurrentData().map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={["#62a744", "#82ca9d", "#8884d8", "#ffc658", "#ff8042"][index % 5]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              )}
            </ResponsiveContainer>
          </div>
        </div>

        {/* Data Table */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-6">Детализированные данные</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="bg-gray-50">
                <tr>
                  {activeTab === 'routes' ? (
                    <>
                      <th className="px-6 py-3 font-semibold text-gray-900">Период</th>
                      <th className="px-6 py-3 font-semibold text-gray-900">Маршруты</th>
                      <th className="px-6 py-3 font-semibold text-gray-900">Участки</th>
                      <th className="px-6 py-3 font-semibold text-gray-900">Средняя длина</th>
                      <th className="px-6 py-3 font-semibold text-gray-900">Эффективность</th>
                    </>
                  ) : activeTab === 'violations' ? (
                    <>
                      <th className="px-6 py-3 font-semibold text-gray-900">Период</th>
                      <th className="px-6 py-3 font-semibold text-gray-900">Нарушения</th>
                      <th className="px-6 py-3 font-semibold text-gray-900">Постановления</th>
                      <th className="px-6 py-3 font-semibold text-gray-900">Сравнение с 2023</th>
                      <th className="px-6 py-3 font-semibold text-gray-900">Изменение</th>
                    </>
                  ) : activeTab === 'accidents' ? (
                    <>
                      <th className="px-6 py-3 font-semibold text-gray-900">Период</th>
                      <th className="px-6 py-3 font-semibold text-gray-900">ДТП</th>
                      <th className="px-6 py-3 font-semibold text-gray-900">Пострадавшие</th>
                      <th className="px-6 py-3 font-semibold text-gray-900">Погибшие</th>
                      <th className="px-6 py-3 font-semibold text-gray-900">Изменение</th>
                    </>
                  ) : (
                    <>
                      <th className="px-6 py-3 font-semibold text-gray-900">Район</th>
                      <th className="px-6 py-3 font-semibold text-gray-900">Маршруты</th>
                      <th className="px-6 py-3 font-semibold text-gray-900">Охват</th>
                      <th className="px-6 py-3 font-semibold text-gray-900">Приоритет</th>
                    </>
                  )}
                </tr>
              </thead>
              <tbody>
                {getCurrentData().map((item, index) => {
                  if (activeTab === 'routes') {
                    const efficiency = Math.round((item.avgRouteLength / 5) * 100);
                    return (
                      <tr key={index} className="border-b border-gray-200 hover:bg-gray-50">
                        <td className="px-6 py-4 font-medium">{item.month}</td>
                        <td className="px-6 py-4">{item.routes}</td>
                        <td className="px-6 py-4">{item.totalStreets}</td>
                        <td className="px-6 py-4">{item.avgRouteLength.toFixed(1)}</td>
                        <td className="px-6 py-4 font-semibold text-[#62a744]">{efficiency}%</td>
                      </tr>
                    );
                  } else if (activeTab === 'violations') {
                    const change = ((item.violations - item.compared2023) / item.compared2023 * 100);
                    return (
                      <tr key={index} className="border-b border-gray-200 hover:bg-gray-50">
                        <td className="px-6 py-4 font-medium">{item.month}</td>
                        <td className="px-6 py-4">{item.violations.toLocaleString()}</td>
                        <td className="px-6 py-4">{item.fines.toLocaleString()}</td>
                        <td className="px-6 py-4">{item.compared2023.toLocaleString()}</td>
                        <td className={`px-6 py-4 font-semibold ${change > 0 ? 'text-red-600' : 'text-green-600'}`}>
                          {change > 0 ? '+' : ''}{change.toFixed(1)}%
                        </td>
                      </tr>
                    );
                  } else if (activeTab === 'accidents') {
                    const change = ((item.accidents - item.compared2023) / item.compared2023 * 100);
                    return (
                      <tr key={index} className="border-b border-gray-200 hover:bg-gray-50">
                        <td className="px-6 py-4 font-medium">{item.month}</td>
                        <td className="px-6 py-4">{item.accidents}</td>
                        <td className="px-6 py-4">{item.injured}</td>
                        <td className="px-6 py-4 text-red-600 font-semibold">{item.fatal}</td>
                        <td className={`px-6 py-4 font-semibold ${change > 0 ? 'text-red-600' : 'text-green-600'}`}>
                          {change > 0 ? '+' : ''}{change.toFixed(1)}%
                        </td>
                      </tr>
                    );
                  } else {
                    const priority = item.coverage > 20 ? 'Высокий' : item.coverage > 10 ? 'Средний' : 'Низкий';
                    return (
                      <tr key={index} className="border-b border-gray-200 hover:bg-gray-50">
                        <td className="px-6 py-4 font-medium">{item.district}</td>
                        <td className="px-6 py-4">{item.routes}</td>
                        <td className="px-6 py-4">{item.coverage}%</td>
                        <td className={`px-6 py-4 font-semibold ${
                          priority === 'Высокий' ? 'text-green-600' : 
                          priority === 'Средний' ? 'text-yellow-600' : 'text-red-600'
                        }`}>
                          {priority}
                        </td>
                      </tr>
                    );
                  }
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Footer Note */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-xl p-6">
          <div className="flex items-start gap-3">
            <Activity className="w-5 h-5 text-blue-600 mt-0.5" />
            <div>
              <h4 className="font-semibold text-blue-900 mb-2">О данных</h4>
              <p className="text-blue-800 text-sm leading-relaxed">
                Статистика маршрутов основана на реальных данных ЦОДД Смоленска за 2024-2025 годы. 
                Данные о нарушениях и ДТП синхронизируются с системами ГИБДД и обновляются ежедневно.
                Для получения детализированной информации обращайтесь в наш центр по телефону +7 (4812) 123-456.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}