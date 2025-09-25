import IncidentMap from "../components/IncidentMap";

export default function Dashboard() {
  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Open Data Dashboard</h2>
      <IncidentMap />
    </div>
  );
}
