import React from "react";

const links = [
  { label: "Home", href: "#" },
  { label: "Analytics", href: "#" },
  { label: "Admin Panel", href: "#" },
];

export default function Sidebar() {
  return (
    <aside className="bg-gray-900 text-gray-200 w-64 min-h-screen hidden md:flex flex-col">
      <div className="px-6 py-4 text-lg font-semibold border-b border-gray-700">
        Menu
      </div>
      <nav className="flex-1 px-4 py-2 space-y-2">
        {links.map((link) => (
          <a
            key={link.label}
            href={link.href}
            className="block px-3 py-2 rounded hover:bg-gray-700 hover:text-white"
          >
            {link.label}
          </a>
        ))}
      </nav>
    </aside>
  );
}


export {}; 