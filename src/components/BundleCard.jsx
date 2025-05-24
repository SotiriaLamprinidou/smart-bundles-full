import React from "react";

export default function BundleCard({ bundle, onAdd }) {
  return (
    <div className="bg-white bg-opacity-90 backdrop-blur-lg shadow-card rounded-2xl p-6 relative hover:shadow-2xl hover:scale-[1.02] transition-transform duration-300 ease-in-out">
      {bundle.recommended && (
        <div className="absolute top-4 right-4 bg-gradient-to-r from-purple-500 to-blue-500 text-white px-3 py-1 rounded-full text-xs font-bold shadow-md">
          Recommended
        </div>
      )}

      <div className="flex justify-center mb-4">
        {bundle.icon}
      </div>

      <h2 className="text-xl font-semibold mb-2 text-center text-primary">
        {bundle.name}
      </h2>

      <p className="text-sm text-gray-600 mb-3 text-center">
        <strong>Includes:</strong> {bundle.products.join(", ")}
      </p>

      <div className="mb-4 text-center">
        <span className="text-gray-400 line-through mr-2">
          ${bundle.originalPrice}
        </span>
        <span className="text-accent font-bold">
          ${bundle.discountedPrice}
        </span>
      </div>

      <div className="flex justify-center">
        <button
  onClick={onAdd}
  className="bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-indigo-600 hover:to-purple-600 text-white px-5 py-2 rounded-xl transition-all duration-200 shadow hover:shadow-lg"
>
  Add to Cart
</button>

      </div>
    </div>
  );
}
