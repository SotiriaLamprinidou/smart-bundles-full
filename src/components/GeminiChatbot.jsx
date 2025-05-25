import { useEffect, useState } from "react";
import { getRecommendations } from "../services/getGeminiRecommendations";
import BundleCard from "./BundleCard";

export default function GeminiChatbot({ cartItems, addToCart }) {
  const [bundles, setBundles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAndAsk = async () => {
      try {
        fetch("http://localhost:5000/api/allBundles")
        const allBundles = await res.json();
        console.log("📦 All bundles from backend:", allBundles);


        const aiBundles = await getRecommendations(cartItems, allBundles);
        setBundles(aiBundles);
      } catch (err) {
        console.error("❌ Gemini error:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchAndAsk();
  }, [cartItems]);

  return (
    <div className="mt-6">
      <h2 className="text-2xl font-bold mb-4 text-center">✨ Personalized AI Suggestions</h2>

      {loading ? (
        <p className="text-center text-gray-500">Loading suggestions...</p>
      )  : (
        <div className="grid gap-6 md:grid-cols-2 mt-6">
          {bundles.map((bundle, i) => (
            <BundleCard
              key={i}
              bundle={{
                name: bundle.title || bundle.name,
                products: bundle.products,
                discountedPrice: bundle.price || 29.99,
                originalPrice: (bundle.price || 29.99) * 1.3,
                recommended: true,
              }}
              onAdd={() =>
                addToCart({
                  name: bundle.title || bundle.name,
                  price: bundle.price || 29.99,
                  discountedPrice: bundle.price || 29.99,
                  products: bundle.products,
                })
              }
            />
          ))}
        </div>
      )}
    </div>
  );
}
