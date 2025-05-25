import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Home from "./pages/Home";
import Bundles from "./pages/Bundles";
import Cart from "./pages/Cart";
import Advisor from "./pages/Advisor";
import CartPopup from "./components/CartPopup";
import IdealMatchBundles from "./components/IdealMatchBundles";
import { getRecommendations } from "./services/getGeminiRecommendations";

function App() {
  const [cartItems, setCartItems] = useState([]);
  const [recentBundle, setRecentBundle] = useState(null);
  const [recommendedItems, setRecommendedItems] = useState(null);

  const addToCart = (bundle) => {
    setCartItems((prev) => {
      const existing = prev.find((item) => item.name === bundle.name);
      if (existing) {
        return prev.map((item) =>
          item.name === bundle.name
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      }
      return [...prev, { ...bundle, quantity: 1 }];
    });

    setRecentBundle(bundle);
    setTimeout(() => setRecentBundle(null), 4000);
  };

  const updateQuantity = (index, delta) => {
    setCartItems((prev) =>
      prev
        .map((item, i) =>
          i === index ? { ...item, quantity: item.quantity + delta } : item
        )
        .filter((item) => item.quantity > 0)
    );
  };

  const removeFromCart = (indexToRemove) => {
    setCartItems((prev) => prev.filter((_, i) => i !== indexToRemove));
  };

  const handleCompleteOrder = async () => {
    if (cartItems.length === 0) {
      alert("Your cart is empty!");
      return;
    }

    try {
      const res = await fetch("/api/allBundles");
      const allBundles = await res.json();
      console.log("✅ Bundles fetched from backend:", allBundles);

      const aiBundles = await getRecommendations(cartItems, allBundles);

      const formatted = aiBundles.map((b) => ({
        name: b.title,
        products: b.products,
        discountedPrice: b.price,
        originalPrice: b.price * 1.15,
      }));

      setRecommendedItems(formatted);
    } catch (err) {
      console.error("❌ Failed to get recommendations:", err);
      alert("Something went wrong while fetching suggestions.");
    }
  };

  const handleReviewComplete = (acceptedItems) => {
    setCartItems((prev) => {
      const updatedCart = [...prev];
      acceptedItems.forEach((bundle) => {
        const existingIndex = updatedCart.findIndex((item) => item.name === bundle.name);
        if (existingIndex !== -1) {
          updatedCart[existingIndex].quantity += 1;
        } else {
          updatedCart.push({ ...bundle, quantity: 1 });
        }
      });
      return updatedCart;
    });
    setRecommendedItems(null);
    alert(`✅ Added ${acceptedItems.length} recommended bundles to your cart!`);
  };

  return (
    <Router>
      {recentBundle && (
        <CartPopup
          bundle={recentBundle}
          onClose={() => setRecentBundle(null)}
        />
      )}

      {Array.isArray(recommendedItems) && recommendedItems.length > 0 && (
        <IdealMatchBundles
          items={recommendedItems}
          onClose={() => setRecommendedItems(null)}
          onComplete={handleReviewComplete}
          addToCart={addToCart}
        />
      )}

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/bundles" element={<Bundles addToCart={addToCart} />} />
        <Route
          path="/cart"
          element={
            <Cart
              cartItems={cartItems}
              removeFromCart={removeFromCart}
              updateQuantity={updateQuantity}
              onCompleteOrder={handleCompleteOrder}
            />
          }
        />
        <Route path="/advisor" element={<Advisor />} />
      </Routes>
    </Router>
  );
}

export default App;
