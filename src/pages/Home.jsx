import React from "react";
import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col justify-center items-center bg-gradient-to-br from-indigo-100 to-purple-100 text-center p-10">
      <h1 className="text-5xl font-display font-bold text-primary mb-10">
        👋 Welcome to SmartBundle AI!
      </h1>
      <div className="space-x-4">
        <Link to="/bundles">
          <button className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-xl shadow">
            View Smart Bundles
          </button>
        </Link>
        <Link to="/cart">
          <button className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-xl shadow">
            Go to Cart
          </button>
        </Link>
        <Link to="/advisor" className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-xl shadow">Advisor</Link>
      </div>
    </div>
  );
}
