# smart-bundles-full
smart-bundles-full
# 🧠 Smart Bundles AI

Smart Bundles AI is an interactive web application designed to help users discover intelligent product bundles that maximize value. It leverages Gemini AI (by Google) to suggest bundle combinations, offer personalized upsells, and provide analytical insights into bundle performance and forecasted revenue.

## 🎥 Demo

Check out the live experience in action:  
📹 [SmartBundleDemoApp.mp4](./Image&Video/SmartBundleDemoApp.mp4)

---

## 🚀 Features

- 🛍️ Smart Bundle Suggestions – Bundles are auto-generated based on product categories, brands, and discounts.
- 🧺 AI-Powered Cart Advisor – Uses Gemini 1.5 to generate personalized upsell suggestions based on items in the cart.
- 🤖 Interactive Chatbot (Advisor) – Ask AI-driven questions like:
  - “Which bundles have the highest forecasted revenue?”
  - “Show me clearance bundles”
  - “What are high AOV suggestions?”
- 📦 Volume, Thematic & Rule-Based Bundles – Bundles generated via different strategies and datasets.
- 📊 Business Logic-Driven Responses – AI answers are shaped based on preloaded business CSV datasets via Flask API.

---

## 🧠 Technologies Used

 Frontend
- React.js (Vite + JSX)
- TailwindCSS for styling
- ShadCN & Lucide Icons for UI components
- Gemini Generative AI SDK (`@google/generative-ai`)
- React Router for navigation

### Backend
- Flask (Python) API to:
  - Load and filter CSV data
  - Predict user intent (via NLP classifier)
  - Feed business context to Gemini
- Scikit-learn for intent classification
- Pandas for bundle dataset processing

---


## 🧪 Example Questions (Chatbot)

- `Show me high AOV bundles`
- `Do you have clearance bundles?`
- `Suggest volume multipacks`
- `Which bundles generate the most revenue?`
- `Any bundle with 10% discount?`

---

## 🧠 How Gemini AI Is Used

1. Cart Advisor (Gemini Recommender): 
   When users view their basket, Gemini receives the selected products and recommends smart bundle additions (using prompt engineering with product metadata).

2. Chatbot Advisor (AOV & Forecast Tool): 
   Queries typed by the user are classified into intents. Then, Gemini receives:
   - Filtered CSV-based context from Flask (e.g. top forecasted bundles)
   - The actual user question  
   It responds with actionable insight, mimicking a business analyst.
