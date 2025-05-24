import React from "react";
import { useNavigate } from "react-router-dom";

export default function CartPopup({ bundle, onClose }) {
  const navigate = useNavigate();

  if (!bundle) return null;

  return (
    <div className="fixed top-6 right-6 z-50 bg-white shadow-lg rounded-xl p-4 border border-blue-200 w-72 animate-fade-in-down">
      <h2 className="text-lg font-bold text-indigo-600">Added to Cart 🛒</h2>
      <p className="text-sm text-gray-700 mt-1">{bundle.name}</p>
      <p className="text-xs text-gray-500">
        {bundle.products?.join(", ") ?? "No products listed"}
      </p>

      <div className="flex justify-end mt-4 gap-2">
        <button
          onClick={onClose}
          className="text-sm text-gray-500 hover:text-gray-700"
        >
          Close
        </button>
        <button
           onClick={() => {
  onClose();
  navigate("/cart");
}}

         
          className="bg-blue-500 hover:bg-blue-600 text-white text-sm px-3 py-1 rounded"
        >
          Go to Cart
        </button>
      </div>
    </div>
  );
}
