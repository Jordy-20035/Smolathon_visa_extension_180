import { BrowserRouter as Router, Routes, Route, Link, useLocation } from "react-router-dom";
import Home from "./pages/Home";
import Admin from "./pages/Admin";
import Login from "./pages/Login";
import Statistics from "./pages/Statistics";
import Dashboard from "./pages/Dashboard";
import { useEffect, useState } from "react";
import ImportData from './pages/ImportData';
import ExportData from './pages/ExportData';


// Create a separate Navigation component to handle auth state
const Navigation = () => {
  const [user, setUser] = useState<any>(null);
  const location = useLocation();

  // Check authentication on component mount and route changes
  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    } else {
      setUser(null);
    }
  }, [location]); // Re-check when route changes

  return (
    <nav className="flex justify-between items-center bg-white shadow-md px-4 py-2 sticky top-0 z-10">
      <Link to="/" className="text-xl font-bold text-gray-900">
        Smolathon
      </Link>
      
      <div className="space-x-4">
        <Link to="/" className="hover:text-blue-600">Home</Link>
        
        {/* Show Dashboard for all logged-in users */}
        {user && (
          <Link to="/dashboard" className="hover:text-blue-600">Dashboard</Link>
        )}
        
        <Link to="/statistics" className="hover:text-blue-600">Statistics</Link>
        
        {/* Show Admin link ONLY for admin/redactor users */}
        {user && (user.role === 'admin' || user.role === 'redactor') && (
          <Link to="/admin" className="hover:text-blue-600">Admin</Link>
        )}
        
        {/* Show Login/Logout based on auth state */}
        {user ? (
          <div className="inline-flex items-center space-x-2">
            <span className="text-sm text-gray-600">Welcome, {user.username}</span>
            <button 
              onClick={() => {
                localStorage.removeItem('user');
                localStorage.removeItem('api_key');
                setUser(null);
                window.location.href = '/';
              }}
              className="px-3 py-1 bg-red-500 text-white rounded-lg hover:bg-red-600 transition text-sm"
            >
              Logout
            </button>
          </div>
        ) : (
          <Link to="/login" className="px-3 py-1 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition">
            Login
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
