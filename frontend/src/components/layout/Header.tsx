import React from "react";

export default function Header() {
  return (
    <header className="bg-white shadow px-6 py-4 flex items-center justify-between">
      <h1 className="text-xl font-bold text-gray-800">🚦 Smolensk Traffic Dashboard</h1>
      <div className="flex items-center space-x-4">
        <span className="text-sm text-gray-600">Guest</span>
        <button className="px-3 py-1 rounded bg-blue-600 text-white hover:bg-blue-700 transition">
          Login
        </button>
      </div>
    </header>
  );
}


export {}; 