import React from "react";

export default function Login() {
  return (
    <div className="max-w-sm mx-auto bg-white shadow p-6 rounded-xl">
      <h1 className="text-xl font-bold mb-4">Login</h1>
      <input
        type="text"
        placeholder="Username"
        className="border rounded-lg px-3 py-2 w-full mb-3"
      />
      <input
        type="password"
        placeholder="Password"
        className="border rounded-lg px-3 py-2 w-full mb-4"
      />
      <button className="bg-blue-600 text-white px-4 py-2 rounded w-full hover:bg-blue-700 transition">
        Sign In
      </button>
    </div>
  );
}
