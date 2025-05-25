import React, { useState, useRef } from "react";
import './IdealMatchBundles.css';
import GeminiChatbot from "./GeminiChatbot";

export default function IdealMatchBundles({ items, onClose, onComplete, addToCart }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [acceptedItems, setAcceptedItems] = useState([]);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [dragging, setDragging] = useState(false);
  const [showMatch, setShowMatch] = useState(false);
  const cardRef = useRef(null);

  if (!items || items.length === 0) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center p-6 z-50">
        <div className="bg-white p-8 rounded-xl max-w-md w-full text-center">
          <h2 className="text-xl font-semibold mb-4">No Items Available</h2>
          <button onClick={onClose} className="btn-primary">Close</button>
        </div>
      </div>
    );
  }

 if (currentIndex >= items.length) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-70 flex flex-col items-center justify-center p-6 z-50 text-center">
      <div className="bg-white p-8 rounded-xl max-w-md w-full">
        <h2 className="text-xl font-semibold mb-4">
          {acceptedItems.length > 0 ? "Selected Items Saved!" : "No Items Selected"}
        </h2>

        {/* 👇 Here is the GeminiChatbot */}
        <div className="my-4">
          <GeminiChatbot cartItems={acceptedItems} addToCart={addToCart} />
        </div>
        <button onClick={onClose} className="btn-primary mt-4">Continue</button>
      </div>
    </div>
  );
}


  const card = items[currentIndex];

  const getClientX = (e) => (e.clientX ?? (e.touches && e.touches[0].clientX));

  const handlePointerDown = (e) => {
    e.preventDefault();
    setDragging(true);
    cardRef.current.startX = getClientX(e);
  };

  const handlePointerMove = (e) => {
    if (!dragging) return;
    const clientX = getClientX(e);
    const deltaX = clientX - cardRef.current.startX;
    setDragOffset({ x: deltaX, y: 0 });
  };

  const goToNextCard = () => {
    setDragOffset({ x: 0, y: 0 });
    setCurrentIndex(prev => prev + 1);
  };

  const handlePointerUp = () => {
    if (!dragging) return;
    setDragging(false);
    const threshold = 100;

    if (dragOffset.x > threshold) {
      setAcceptedItems(prev => [...prev, card]);
      if (addToCart) addToCart(card);
      setShowMatch(true);
      setTimeout(() => {
        setShowMatch(false);
        goToNextCard();
      }, 800);
    } else if (dragOffset.x < -threshold) {
      goToNextCard();
    } else {
      setDragOffset({ x: 0, y: 0 });
    }
  };

  const swipeClass = dragOffset.x > 0 ? "card-swipe-right" : dragOffset.x < 0 ? "card-swipe-left" : "";

  return (
    <>
      {showMatch && (
        <div className="fullpage-match-overlay">
          <div className="match-text">It's a Match! 🎉</div>
        </div>
      )}

      <div className="fixed inset-0 bg-black bg-opacity-70 flex flex-col items-center justify-center p-6 z-50">
        <button onClick={onClose} className="btn-close absolute top-4 right-4" aria-label="Close">✕</button>

        <div
          ref={cardRef}
          onMouseDown={handlePointerDown}
          onTouchStart={handlePointerDown}
          onMouseMove={handlePointerMove}
          onTouchMove={handlePointerMove}
          onMouseUp={handlePointerUp}
          onTouchEnd={handlePointerUp}
          onMouseLeave={handlePointerUp}
          className={`card-container rounded-xl shadow-xl select-none ${swipeClass}`}
          style={{
            height: "600px",
            maxWidth: "450px",
            userSelect: "none",
            cursor: dragging ? "grabbing" : "grab",
            transform: `translateX(${dragOffset.x}px) rotate(${dragOffset.x / 20}deg)`,
            transition: dragging ? "none" : "transform 0.3s ease",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            padding: "2rem",
            boxSizing: "border-box",
          }}
        >
          <h2 className="card-title-gradient">{card.name}</h2>

          <div style={{ textAlign: "left" }}>
            <p className="card-includes-label">Includes:</p>
            <ul className="card-products list-none pl-0 mb-6">
              {card.products.map((product, i) => (
                <li key={i} className="product-item">{product}</li>
              ))}
            </ul>
          </div>

          <p className="card-price">
            €{card.discountedPrice.toFixed(2)}
            {card.originalPrice && (
              <span className="card-original-price">€{card.originalPrice.toFixed(2)}</span>
            )}
          </p>
        </div>

        <p className="mt-4 text-white select-none">
          Drag right to accept, drag left to skip
        </p>
      </div>
    </>
  );
}
