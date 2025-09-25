export default function Navbar() {
  return (
    <nav className="bg-gray-800 text-white px-4 py-3 flex justify-between">
      <div className="font-bold text-lg">🚦 Smolensk TMC</div>
      <div className="space-x-4">
        <a href="/" className="hover:underline">Home</a>
        <a href="/dashboard" className="hover:underline">Dashboard</a>
        <a href="/services" className="hover:underline">Services</a>
        <a href="/admin" className="hover:underline">Admin</a>
      </div>
    </nav>
  );
}
