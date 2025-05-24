import React from "react";
import { useNavigate } from "react-router-dom";
import { ArrowBigLeft } from "lucide-react";
import BundleCard from "../components/BundleCard";
import { Monitor, Coffee, Gamepad2, Leaf, Music, Package } from "lucide-react";

// bundle data stays the same...
const bundles = [
  {
    name: "Work From Home Essentials",
    icon: <Monitor size={56} className="text-indigo-500 mb-4" />,
    products: ["Wireless Mouse", "Laptop Stand", "Noise-Cancelling Headphones"],
    originalPrice: 210,
    discountedPrice: 159,
    recommended: true,
  },
  {
    name: "Morning Routine Kit",
    icon: <Coffee size={56} className="text-blue-500 mb-4" />,
    products: ["Electric Toothbrush", "Vitamin C Serum", "Coffee Grinder"],
    originalPrice: 140,
    discountedPrice: 110,
    recommended: false,
  },
  {
    name: "Gaming Pro Pack",
    icon: <Gamepad2 size={56} className="text-purple-500 mb-4" />,
    products: ["Gaming Chair", "Mechanical Keyboard", "RGB Mousepad"],
    originalPrice: 340,
    discountedPrice: 289,
    recommended: true,
  },
  {
    name: "Eco Wellness Bundle",
    icon: <Leaf size={56} className="text-green-500 mb-4" />,
    products: ["Reusable Water Bottle", "Yoga Mat", "Essential Oils"],
    originalPrice: 120,
    discountedPrice: 95,
    recommended: false,
  },
  {
    name: "Lo-Fi Music Starter Pack",
    icon: <Music size={56} className="text-pink-500 mb-4" />,
    products: ["Bluetooth Speaker", "Noise-Isolating Headphones", "Spotify Gift Card"],
    originalPrice: 180,
    discountedPrice: 149,
    recommended: true,
  },
  {
    name: "Ultimate Unboxing Deal",
    icon: <Package size={56} className="text-cyan-500 mb-4" />,
    products: ["Mystery Tech", "Gift Card", "Bonus Surprise"],
    originalPrice: 250,
    discountedPrice: 199,
    recommended: false,
  },
];

export default function Bundles({ addToCart }) {
  const navigate = useNavigate();

  return (
    <div className="relative min-h-screen bg-gradient-to-tr from-indigo-100 via-blue-100 to-purple-100 p-10 font-body">
      {/* Back Button */}
      <div className="absolute top-6 left-6">
        <button
          onClick={() => navigate("/")}
          className="bg-blue-500 hover:bg-blue-600 text-white p-3 rounded-full shadow-lg transition"
          aria-label="Go back"
        >
          <ArrowBigLeft size={24} />
        </button>
      </div>

      {/* Page Title */}
      <h1 className="text-5xl font-display font-extrabold mb-10 text-center text-transparent bg-clip-text bg-gradient-to-r from-indigo-500 via-blue-500 to-purple-500">
        🔥 Smart Bundles Just for You
      </h1>

      {/* Bundle Cards */}
      <div className="grid gap-6 md:grid-cols-3">
        {bundles.map((bundle, i) => (
          <BundleCard key={i} bundle={bundle} onAdd={() => addToCart(bundle)} />
        ))}
      </div>
    </div>
  );
}
