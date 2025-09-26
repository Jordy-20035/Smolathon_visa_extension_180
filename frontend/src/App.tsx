import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Home from "./pages/Home";
import Admin from "./pages/Admin";
import Login from "./pages/Login";
import Statistics from "./pages/Statistics";

function App() {
  return (
    <Router>
      {/* Navbar */}
      <nav className="flex justify-between items-center bg-white shadow-md px-4 py-2 sticky top-0 z-10">
        <Link to="/" className="text-xl font-bold text-gray-900">
          Smolathon
        </Link>
        <div className="space-x-4">
          <Link to="/" className="hover:text-blue-600">
            Home
          </Link>
          <Link to="/admin" className="hover:text-blue-600">
            Admin
          </Link>
          <Link to="/statistics" className="hover:text-blue-600">
            Statistics
          </Link>
          <Link
            to="/login"
            className="px-3 py-1 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
          >
            Login
          </Link>
        </div>
      </nav>

      {/* Main content */}
      <main className="p-4">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/admin" element={<Admin />} />
          <Route path="/statistics" element={<Statistics />} />
          <Route path="/login" element={<Login />} />
        </Routes>
      </main>

      {/* Footer */}
      <footer className="text-center py-4 text-sm text-gray-500">
        © 2025 Smolathon Hackathon — All Rights Reserved
      </footer>
    </Router>
  );
}

export default App;
