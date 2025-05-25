import React, { useState } from "react";
import { GoogleGenerativeAI } from "@google/generative-ai";
import { useNavigate } from "react-router-dom";
import { ArrowBigLeft } from "lucide-react";

const genAI = new GoogleGenerativeAI(import.meta.env.VITE_GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

export default function Advisor() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!userInput.trim()) return;

    const userMessage = { role: "user", text: userInput };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      // 🔁 Φέρνουμε context με βάση την ερώτηση
      const res = await fetch(`/api/advisor-data?question=${encodeURIComponent(userInput)}`);
      const data = await res.json();

      const prompt = `
📊 Business Data:
${data.context}

🧠 Ερώτηση χρήστη:
${userInput}

Απάντησε όσο πιο περιεκτικά γίνεται με βάση τα δεδομένα.
      `;

      const result = await model.generateContent(prompt);
      const reply = await result.response.text();

      setMessages((prev) => [...prev, { role: "ai", text: reply }]);
    } catch (err) {
      console.error("❌ Failed to fetch or generate:", err);
      setMessages((prev) => [
        ...prev,
        { role: "ai", text: "⚠️ Παρουσιάστηκε πρόβλημα. Προσπάθησε ξανά." },
      ]);
    }

    setUserInput("");
    setLoading(false);
  };

  return (
    <div className="relative min-h-screen bg-gradient-to-tr from-indigo-100 via-blue-100 to-purple-100 p-10 font-body">

      <h1 className="text-3xl font-bold mb-6 text-center">📈 AOV & Bundle Boost Advisor</h1>

      {/* Back Button */}
      <div className="absolute top-6 left-6">
        <button
          onClick={() => navigate("/")}
          className="bg-blue-500 hover:bg-blue-600 text-white p-3 rounded-full shadow-lg"
          aria-label="Go back"
        >
          <ArrowBigLeft size={24} />
        </button>
      </div>

      <div className="bg-gray-100 rounded-lg p-4 h-[400px] overflow-y-auto mb-4 shadow-inner">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`mb-3 p-3 rounded-lg ${
              msg.role === "user" ? "bg-white text-right" : "bg-blue-100 text-left"
            }`}
          >
            <p>{msg.text}</p>
          </div>
        ))}

        {loading && (
          <div className="text-gray-500 text-sm italic">⏳ Γράφει απάντηση...</div>
        )}
      </div>

      <div className="flex gap-2">
        <input
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          placeholder="Ρώτησε κάτι για τα bundles..."
          className="flex-1 p-2 rounded border"
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />
        <button
          onClick={handleSend}
          className="bg-indigo-500 text-white px-4 py-2 rounded disabled:opacity-50"
          disabled={loading}
        >
          Send
        </button>
      </div>
    </div>
  );
}
