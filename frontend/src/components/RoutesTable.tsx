// src/components/RoutesTable.tsx
import { useState } from "react";
import { routesData, RouteRecord } from "../data/routes";

export default function RoutesTable() {
  const [year, setYear] = useState<number | "all">("all");
  const [month, setMonth] = useState<string>("");

  const filteredData = routesData.filter((item) => {
    return (year === "all" || item.year === year) &&
           (month === "" || item.month === month);
  });

  return (
    <div className="p-6">
      <div className="flex gap-4 mb-4">
        <select
          value={year}
          onChange={(e) => setYear(e.target.value === "all" ? "all" : Number(e.target.value))}
          className="border p-2 rounded"
        >
          <option value="all">Все года</option>
          <option value="2024">2024</option>
          <option value="2025">2025</option>
        </select>

        <select
          value={month}
          onChange={(e) => setMonth(e.target.value)}
          className="border p-2 rounded"
        >
          <option value="">Все месяцы</option>
          {Array.from(new Set(routesData.filter(r => year === "all" || r.year === year).map(r => r.month)))
            .map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
        </select>
      </div>

      <div className="grid gap-4">
        {filteredData.map((item, index) => (
          <div key={index} className="border rounded-2xl p-4 shadow">
            <h2 className="font-bold text-lg mb-2">{item.year} – {item.month}</h2>
            <ul className="list-disc list-inside">
              {item.route.map((street, idx) => (
                <li key={idx}>{street}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
