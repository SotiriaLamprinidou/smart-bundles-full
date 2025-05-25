import { GoogleGenerativeAI } from "@google/generative-ai";

const genAI = new GoogleGenerativeAI(import.meta.env.VITE_GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

export const getRecommendations = async (cartItems, allBundles = []) => {
  // 1. Εξαγωγή λίστας προϊόντων του καλαθιού
  const productList = cartItems.flatMap(item => item.products);
  const productText = productList.join(", ");

  // 2. Εξαγωγή πιθανών όρων σύγκρισης για συνάφεια
  const keywords = productList
    .map((p) => p.split(" ")[0]) // πρώτο keyword από κάθε τίτλο
    .filter(Boolean);

  // 3. Φιλτράρισμα bundles με λέξεις-κλειδιά για σχετικότητα
  const relevantBundles = allBundles.filter((bundle) =>
    keywords.some((kw) =>
      bundle["Suggested Bundle Title"].toLowerCase().includes(kw.toLowerCase())
    )
  );

  const limitedBundles = relevantBundles.slice(0, 100); // για ασφάλεια token

  // 4. Δημιουργία λίστας bundles σε μορφή prompt
  const availableBundleList = limitedBundles
    .map(
      (b, i) =>
        `${i + 1}. [${b.BundleType}] ${b["Suggested Bundle Title"]} – €${b.FinalPrice.toFixed(2)}`
    )
    .join("\n");

  // 5. Prompt προς Gemini
  const prompt = `
Ένας πελάτης έχει στο καλάθι του τα εξής προϊόντα:
${productText}

Από τα παρακάτω διαθέσιμα bundles, πρότεινε 3 που ταιριάζουν πραγματικά με βάση:
- κοινό brand ή προϊόν
- παρόμοια χρήση ή κατηγορία
- απόλυτη συνάφεια με το καλάθι του

❗ ΜΗΝ εφευρίσκεις νέα προϊόντα ή bundles. Διάλεξε **μόνο** από τα παρακάτω.

Μη χρησιμοποιείς τη λέξη Δώρο στον τίτλο.

Απάντησε αυστηρά σε JSON array:
[
  {
    "title": "Bundle Title",
    "products": ["Product A", "Product B"],
    "price": 19.99
  }
]

📦 Διαθέσιμα Bundles:
${availableBundleList}
`;

  try {
    console.log("🧠 Gemini Prompt:\n", prompt);

    const result = await model.generateContent(prompt);
    const text = await result.response.text();

    // Εξαγωγή JSON από την απάντηση
    const start = text.indexOf("[");
    const end = text.lastIndexOf("]") + 1;
    const jsonString = text.slice(start, end);

    const parsed = JSON.parse(jsonString);

    // Προσθήκη backup τιμής αν λείπει
    return parsed.map((bundle) => ({
      ...bundle,
      price: bundle.price ?? 29.99,
    }));
  } catch (e) {
    console.error("❌ Gemini parsing failed:", e);
    return [];
  }
};
