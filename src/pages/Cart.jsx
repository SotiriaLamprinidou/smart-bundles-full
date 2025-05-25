import React from "react";
import { ArrowBigLeft, X } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Cart({ cartItems, removeFromCart, updateQuantity, onCompleteOrder }) {
  const navigate = useNavigate();

  const subtotal = cartItems.reduce(
    (sum, item) => sum + item.discountedPrice * item.quantity,
    0
  );
  const vat = subtotal * 0.2;
  const total = subtotal + vat;

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-blue-100 to-purple-100 font-body p-10">
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

      <h1 className="text-4xl font-display font-bold text-primary mb-10 text-center mt-10">
        🛒 Your Cart
      </h1>

      {cartItems.length === 0 ? (
        <p className="text-center text-gray-600 text-lg mt-20">
          Looks like your cart is empty.
        </p>
      ) : (
        <div className="flex flex-col lg:flex-row justify-center gap-10 mt-10">
          {/* Cart Items */}
          <ul className="space-y-4 w-full max-w-2xl">
            {cartItems.map((item, index) => (
              <li key={index} className="relative bg-white rounded-xl p-4 shadow">
                {/* Remove Button */}
                <button
                  onClick={() => removeFromCart(index)}
                  className="absolute top-3 right-3 text-gray-400 hover:text-red-500 transition"
                  aria-label="Remove item"
                >
                  <X size={20} />
                </button>

                <h2 className="text-lg font-semibold text-indigo-600">{item.name}</h2>

                {Array.isArray(item.products) && item.products.length > 0 && (
                  <ul className="text-sm text-gray-600 list-disc list-inside mt-1">
                    {item.products.map((product, i) => (
                      <li key={i}>{product}</li>
                    ))}
                  </ul>
                )}

                <p className="font-bold text-accent mt-2">
                  €{item.discountedPrice.toFixed(2)} each
                </p>

                <div className="flex justify-between items-center mt-3">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => updateQuantity(index, -1)}
                      className="bg-gray-200 hover:bg-gray-300 text-gray-700 rounded px-2"
                      disabled={item.quantity <= 1}
                    >
                      −
                    </button>
                    <span className="text-sm font-medium">{item.quantity}</span>
                    <button
                      onClick={() => updateQuantity(index, 1)}
                      className="bg-gray-200 hover:bg-gray-300 text-gray-700 rounded px-2"
                    >
                      +
                    </button>
                  </div>
                  <p className="font-bold text-accent">
                    €{(item.discountedPrice * item.quantity).toFixed(2)}
                  </p>
                </div>
              </li>
            ))}
          </ul>

          {/* Order Summary */}
          <div className="bg-white rounded-xl shadow p-6 w-full max-w-sm h-fit">
            <h2 className="text-xl font-semibold text-indigo-600 mb-4">
              Order Summary
            </h2>
            <div className="space-y-2 text-sm text-gray-700">
              <div className="flex justify-between">
                <span>Items:</span>
                <span>{cartItems.reduce((sum, item) => sum + item.quantity, 0)}</span>
              </div>
              <div className="flex justify-between">
                <span>Subtotal:</span>
                <span>€{subtotal.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span>VAT (20%):</span>
                <span>€{vat.toFixed(2)}</span>
              </div>
              <div className="flex justify-between font-bold text-primary border-t pt-2 mt-2">
                <span>Total:</span>
                <span>€{total.toFixed(2)}</span>
              </div>
            </div>

            <button
              onClick={onCompleteOrder}
              className="mt-6 w-full bg-indigo-500 hover:bg-indigo-600 text-white py-2 rounded-xl transition"
            >
              Complete Order
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
