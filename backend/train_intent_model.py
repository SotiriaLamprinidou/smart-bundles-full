# train_intent_model.py
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# 1. Δείγματα ερωτήσεων & κατηγορίες
training_examples = [
    ("Which bundles are more expensive?", "price"),
    ("Show me high margin bundles", "price"),
    ("Give me the most discounted bundles", "price"),
    ("Which bundles increase order value?", "aov"),
    ("What improves AOV?", "aov"),
    ("Top selling bundles", "rule"),
    ("Best forecasted bundles", "forecast"),
    ("Predicted revenue of bundles", "forecast"),
    ("What are the clearance bundles?", "clearance"),
    ("Overstock bundles", "clearance"),
    ("Are there summer or seasonal bundles?", "thematic"),
    ("Any gift suggestions?", "thematic"),
    ("Are there multipacks?", "volume"),
    ("Show me volume offers", "volume")
]

# 2. Διαχωρισμός features/labels
texts, labels = zip(*training_examples)

# 3. Vectorizer + Training
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)

clf = LogisticRegression()
clf.fit(X, labels)

# 4. Αποθήκευση μοντέλου
joblib.dump(vectorizer, "intent_vectorizer.joblib")
joblib.dump(clf, "intent_classifier.joblib")

print("✅ NLP μοντέλο εκπαιδεύτηκε και αποθηκεύτηκε.")
