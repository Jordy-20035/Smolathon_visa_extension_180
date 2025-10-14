import { BrowserRouter as Router, Routes, Route, Link, useLocation } from "react-router-dom";
import Home from "./pages/Home";
import Admin from "./pages/Admin";
import Login from "./pages/Login";
import Statistics from "./pages/Statistics";
import Dashboard from "./pages/Dashboard";
import { useEffect, useState } from "react";
import ImportData from './pages/ImportData';
import ExportData from './pages/ExportData';


// Navigation component to handle auth state
const Navigation = () => {
  const [user, setUser] = useState<any>(null);
  const location = useLocation();

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    } else {
      setUser(null);
    }
  }, [location]);

  return (
    <nav className="flex justify-between items-center bg-gradient-to-r from-green-600 to-green-700 shadow-lg px-6 py-3 sticky top-0 z-10">
      {/* Logo/Brand */}
      <Link to="/" className="flex items-center space-x-2">
        <span className="text-xl font-bold text-white">ЦОДД Смоленск</span>
      </Link>
      
      {/* Navigation Links */}
      <div className="flex items-center space-x-6">
        <Link to="/" className="text-white hover:text-green-200 transition font-medium">Главная</Link>
        
        {/* Show Dashboard ONLY for admins */}
        {user && user.role === 'admin' && (
          <Link to="/dashboard" className="text-white hover:text-green-200 transition font-medium">Дашборд</Link>
        )}
        
        <Link to="/statistics" className="text-white hover:text-green-200 transition font-medium">Статистика</Link>
        
        {/* Show Admin link ONLY for admin users (NOT editors) */}
        {user && user.role === 'admin' && (
          <Link to="/admin" className="text-white hover:text-green-200 transition font-medium">Админ</Link>
        )}
        
        {/* Show Content Management for editors */}
        {user && user.role === 'redactor' && (
          <Link to="/admin" className="text-white hover:text-green-200 transition font-medium">
            Управление контентом
          </Link>
        )}
        
        {/* Language Switcher */}
        <button className="text-white hover:text-green-200 transition font-medium border border-white px-2 py-1 rounded text-sm">
          EN/RU
        </button>
        
        {/* User Section */}
        {user ? (
          <div className="flex items-center space-x-3">
            <div className="text-white text-sm">
              <span className="font-medium">{user.username}</span>
              <span className="text-green-200 ml-2">({user.role})</span>
            </div>
            <button 
              onClick={() => {
                localStorage.removeItem('user');
                localStorage.removeItem('api_key');
                setUser(null);
                window.location.href = '/';
              }}
              className="px-3 py-1 bg-white text-green-700 rounded-lg hover:bg-green-100 transition font-medium text-sm"
            >
              Выйти
            </button>
          </div>
        ) : (
          <Link to="/login" className="px-4 py-2 bg-white text-green-700 rounded-lg hover:bg-green-100 transition font-medium">
            Войти
          </Link>
        )}
      </div>
    </nav>
  );
};

function App() {
  return (
    <Router>
      <Navigation />
      
      {/* Main content */}
      <main className="p-4 min-h-screen bg-gray-50">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/admin" element={<Admin />} />
          <Route path="/statistics" element={<Statistics />} />
          <Route path="/login" element={<Login />} />
          <Route path="/admin/import" element={<ImportData />} />
          <Route path="/admin/export" element={<ExportData />} />
          
        </Routes>
      </main>

      {/* Footer */}
      <footer className="text-center py-4 text-sm text-gray-500 bg-white border-t">
        © 2025 Smolathon Hackathon — All Rights Reserved
      </footer>
    </Router>
  );
}

export default App;
