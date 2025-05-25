import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowBigLeft,
  Droplet,
  Shirt,
  Bed,
  ToyBrick,
  UtensilsCrossed,
  Package,
} from "lucide-react";
import BundleCard from "../components/BundleCard";

const categoryIcons = {
  "Beauty Kit": <Droplet size={56} className="text-pink-400 mb-4" />,
  "Clothing Pack": <Shirt size={56} className="text-indigo-500 mb-4" />,
  "Home Sweet Home": <Bed size={56} className="text-green-500 mb-4" />,
  "Kids Paradise": <ToyBrick size={56} className="text-yellow-500 mb-4" />,
  "Kitchen Essentials": <UtensilsCrossed size={56} className="text-blue-500 mb-4" />,
  "Smart Bundle": <Package size={56} className="text-purple-500 mb-4" />,
};

const brandCategoryMap = {
  Gant: "Clothing Pack",
  OVS: "Clothing Pack",
  Lacoste: "Clothing Pack",
  Adidas: "Clothing Pack",
  Tommy: "Clothing Pack",
  Timberland: "Clothing Pack",
  "Levi's": "Clothing Pack",
  Guess: "Clothing Pack",
  Kiko: "Beauty Kit",
  Armani: "Beauty Kit",
  DKNY: "Beauty Kit",
  Bvlgari: "Beauty Kit",
  Shiseido: "Beauty Kit",
  Clinique: "Beauty Kit",
  "Narciso Rodriguez": "Beauty Kit",
  Coincasa: "Home Sweet Home",
  Kentia: "Home Sweet Home",
  Funky: "Home Sweet Home",
  "NEF-NEF": "Home Sweet Home",
  Alouette: "Kids Paradise",
  DPAM: "Kids Paradise",
  Mayoral: "Kids Paradise",
  Guzzini: "Kitchen Essentials",
};

function extractBrand(product, brandMap) {
  return Object.keys(brandMap).find((brand) =>
    product.toLowerCase().includes(brand.toLowerCase())
  );
}

function getSmartTitle(products, offerLabel, brandMap) {
  const brands = products.map((p) => extractBrand(p, brandMap)).filter(Boolean);
  const unique = [...new Set(brands)];

  if (unique.length === 1) {
    const brand = unique[0];
    return `${offerLabel} ${brand} ${brandMap[brand]}`;
  }

  for (let brand of brands) {
    if (brandMap[brand]) return `${offerLabel} ${brandMap[brand]}`;
  }

  return `${offerLabel} Smart Bundle`;
}

export default function Bundles({ addToCart }) {
  const navigate = useNavigate();
  const [bundles, setBundles] = useState([]);

  useEffect(() => {
    fetch("/api/bundles")
      .then((res) => res.json())
      .then((data) => {
        const sorted = [...data].sort(
          (a, b) => parseFloat(b.DiscountRate) - parseFloat(a.DiscountRate)
        );
        const topRecommended = sorted.slice(0, 2).map((b) => b["Suggested Bundle Title"]);

        const withFlags = data.map((bundle) => ({
          ...bundle,
          isRecommended: topRecommended.includes(bundle["Suggested Bundle Title"]),
        }));

        setBundles(withFlags);
      })
      .catch((err) => console.error("❌ Αποτυχία φόρτωσης bundles:", err));
  }, []);

  return (
    <div className="relative min-h-screen bg-gradient-to-tr from-indigo-100 via-blue-100 to-purple-100 p-10 font-body">
      <div className="absolute top-6 left-6">
        <button
          onClick={() => navigate("/")}
          className="bg-blue-500 hover:bg-blue-600 text-white p-3 rounded-full shadow-lg transition"
        >
          <ArrowBigLeft size={24} />
        </button>
      </div>

      <h1 className="text-5xl font-display font-extrabold mb-10 text-center text-transparent bg-clip-text bg-gradient-to-r from-indigo-500 via-blue-500 to-purple-500">
        🔥 Smart Bundles Just for You
      </h1>

      <div className="grid gap-6 md:grid-cols-3">
        {bundles.length === 0 ? (
          <p className="text-center col-span-3 text-xl">Φόρτωση...</p>
        ) : (
          bundles.map((bundle, i) => {
            const discount = parseFloat(bundle.DiscountRate || 0);
            const final = parseFloat(bundle.FinalPrice);
            const original = parseFloat(
              (bundle.FullPrice || final / (1 - discount)).toFixed(2)
            );

            const productList = bundle["Suggested Bundle Title"].split(" + ").map((t) => t.trim());
            const smartTitle = getSmartTitle(productList, bundle.OfferLabel, brandCategoryMap);
            const brandMatch = extractBrand(productList[0], brandCategoryMap);
            const category = brandMatch ? brandCategoryMap[brandMatch] : "Smart Bundle";

            return (
              <BundleCard
                key={i}
                bundle={{
                  name: smartTitle,
                  icon: categoryIcons[category] || categoryIcons["Smart Bundle"],
                  products: productList,
                  originalPrice: original,
                  discountedPrice: final,
                  recommended: bundle.isRecommended,
                }}
                onAdd={() =>
                  addToCart({
                    name: smartTitle,
                    price: final,
                    discountedPrice: final,
                    products: productList,
                  })
                }
              />
            );
          })
        )}
      </div>
    </div>
  );
}
