import React from "react";
import RoutesTable from "../components/RoutesTable";

export default function Dashboard() {
  return (
    <main className="flex-1 p-6 bg-gray-50 min-h-screen">
      <h2 className="text-2xl font-bold mb-4">Маршруты</h2>
      <div className="bg-white shadow rounded-2xl p-4">
        <RoutesTable />
      </div>
    </main>
  );
}
