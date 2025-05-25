#backend
from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)


import random

import os

base_dir = os.path.dirname(__file__)
file_path = os.path.join(base_dir, "data", "DATA - AI-Powered Bundling & Pricing Strategist.xlsx")


#file_path = r"C:\Users\Lampr\OneDrive - unipi.gr\Desktop\DataCleansing\DATA - AI-Powered Bundling & Pricing Strategist.xlsx"

#Load data
import numpy as np


# Load both sheets
orders_df = pd.read_excel(file_path, sheet_name='orders')
inventory_df = pd.read_excel(file_path, sheet_name='inventory')

# === 1. Clean Orders Data ===
orders_df.drop_duplicates(inplace=True)

# Μετατροπή Quantity σε αριθμητικό και φιλτράρισμα θετικών τιμών
orders_df['Quantity'] = pd.to_numeric(orders_df['Quantity'], errors='coerce')
orders_df = orders_df[orders_df['Quantity'] > 0]

# Αφαίρεση γραμμών με κρίσιμα missing values
orders_df.dropna(subset=['OrderNumber', 'SKU', 'Item title', 'Quantity'], inplace=True)

# Καθαρισμός ονομάτων στηλών (αφαίρεση κενών χαρακτήρων)
orders_df.columns = [col.strip() for col in orders_df.columns]
inventory_df.columns = [col.strip() for col in inventory_df.columns]

# === 1.1 Remove gifts and zero-price products ===
# Αφαίρεση προϊόντων που είναι πιθανώς promotional (δωρεάν, δείγματα)
gift_keywords = ['gift', 'δώρο', 'sample', 'miniature']
pattern = '|'.join(gift_keywords)

orders_df = orders_df[~orders_df['Item title'].str.lower().str.contains(pattern)]
orders_df = orders_df[orders_df['FinalUnitPrice'] > 0]

# === 2. Clean Inventory Data ===
inventory_df = inventory_df.dropna(subset=['SKU', 'Quantity'])
inventory_df = inventory_df[inventory_df['Quantity'] > 0]
inventory_df.to_csv("data/inventory.csv", index=False)

# Ορισμός διαθέσιμων SKU για μεταγενέστερη χρήση
valid_skus = inventory_df['SKU'].unique()
available_skus_set = set(valid_skus)

# === 3. Merge Orders with Inventory Info ===
orders_df = orders_df.merge(inventory_df, on="SKU", how="left")
orders_df.rename(columns={'Quantity_x': 'OrderQuantity', 'Quantity_y': 'InventoryQuantity'}, inplace=True)
orders_df['InventoryQuantity'] = orders_df['InventoryQuantity'].fillna(0)
orders_df['SKU_in_stock'] = orders_df['InventoryQuantity'] > 0

# === 4. Filter Only SKUs with Enough Frequency for Modeling ===
# Ισορροπία ανάμεσα σε κάλυψη και ποιότητα
min_order_count = 1
sku_order_counts = orders_df.groupby('SKU')['OrderNumber'].nunique()
frequent_skus = sku_order_counts[sku_order_counts >= min_order_count].index
orders_df = orders_df[orders_df['SKU'].isin(frequent_skus)]

# === 5. Optional Sampling for Basket Algorithms ===
sample_size = 130000  # για FP-Growth ή Apriori
unique_orders = orders_df['OrderNumber'].drop_duplicates()
if len(unique_orders) > sample_size:
    sampled_orders = unique_orders.sample(sample_size, random_state=42)
    orders_df = orders_df[orders_df['OrderNumber'].isin(sampled_orders)]

# === 6. Final Info ===
print(f"🧾 Orders after cleaning: {orders_df.shape[0]}")
print(f"✅ Unique Orders: {orders_df['OrderNumber'].nunique()}")
print(f"📦 SKUs in stock: {orders_df['SKU_in_stock'].sum()}")
print(f"⚠️ SKUs out of stock: {(~orders_df['SKU_in_stock']).sum()}")

orders_df['ProductID'] = orders_df['SKU'].astype(str) + ' - ' + orders_df['Item title']

# === 6.1 Create unique ProductID ===
# Συνδυάζει SKU + Item title για να ξεχωρίζεις παραλλαγές


# === 7. Rule-Based Bundle Generation (Top-Sellers + Same Brand) ===

# Βρες τα Top 50 προϊόντα με βάση το συνολικό OrderQuantity
top_products = (
    orders_df.groupby('ProductID')['OrderQuantity'].sum()
    .sort_values(ascending=False)
    .head(50)
    .index
)

# Πίνακας αναφοράς προϊόντων (χωρίς διπλότυπα)
product_info = orders_df.drop_duplicates(subset='ProductID')[
    ['ProductID', 'Brand', 'Category', 'SKU', 'Item title']
].set_index('ProductID')

# Δημιουργία candidate bundles με βάση ίδιο Brand
bundle_candidates = []

for prod_id in top_products:
    brand = product_info.loc[prod_id, 'Brand']

    # Βρες έως 3 σχετικά προϊόντα του ίδιου brand (εκτός του ίδιου προϊόντος)
    related_products = product_info[
        (product_info['Brand'] == brand) &
        (product_info.index != prod_id)
    ].index[:3]

    for related_id in related_products:
        bundle_candidates.append((prod_id, related_id))
# === Εμφάνιση Αποτελεσμάτων ===
print(f"\n📦 Συνολικά δημιουργήθηκαν {len(bundle_candidates)} candidate bundles.")
print("🧠 Rule-based Bundles (Top-sellers + Same Brand):")
for a, b in bundle_candidates[:10]:
    title_a = product_info.loc[a, 'Item title']
    title_b = product_info.loc[b, 'Item title']
    print(f"👉 {title_a} + {title_b}")


# 🔄 Convert tuple list to DataFrame and enrich with titles
bundle_rows = []

for a, b in bundle_candidates:
    bundle_rows.append({
        "Primary Product ID": a,
        "Primary Title": product_info.loc[a, 'Item title'],
        "Bundled With Product ID": b,
        "Bundled With Title": product_info.loc[b, 'Item title'],
        "Brand": product_info.loc[a, 'Brand']
    })

# 📤 Convert to DataFrame
top_seller_bundles_df = pd.DataFrame(bundle_rows)

# 💾 Save as CSV for chatbot input
top_seller_bundles_df.to_csv("top_seller_bundles.csv", index=False)
print("✅ Exported bundle suggestions to 'top_seller_bundles.csv'")

# === Δημιουργία DataFrame από τα υπάρχοντα bundle_candidates ===
rule_bundles_df = pd.DataFrame(bundle_candidates, columns=['ProductID_A', 'ProductID_B'])

# Πίνακας αναφοράς προϊόντων
product_info = orders_df.drop_duplicates(subset='ProductID')[
    ['ProductID', 'Brand', 'Category', 'SKU', 'Item title']
].set_index('ProductID')

# Merge για να φέρουμε τίτλους και SKUs
rule_bundles_df = rule_bundles_df.merge(product_info, left_on='ProductID_A', right_index=True)
rule_bundles_df = rule_bundles_df.merge(product_info, left_on='ProductID_B', right_index=True, suffixes=('_A', '_B'))

# Δημιουργία bundle τίτλου και τύπου
rule_bundles_df['Suggested Bundle Title'] = rule_bundles_df['Item title_A'] + " + " + rule_bundles_df['Item title_B']
rule_bundles_df['BundleType'] = 'Rule-Based'

# Έλεγχος
print(f"\n📦 Δημιουργήθηκε rule_bundles_df με {len(rule_bundles_df)} γραμμές.")
print(rule_bundles_df.head())

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import itertools

# === 1. Πάρε μοναδικούς τίτλους προϊόντων ===
product_titles = orders_df[['ProductID', 'Item title']].drop_duplicates().reset_index(drop=True)

# === 2. TF-IDF Vectorization ===
vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
tfidf_matrix = vectorizer.fit_transform(product_titles['Item title'])

# === 3. KMeans Clustering ===
num_clusters = 5
kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init='auto')
product_titles['Cluster'] = kmeans.fit_predict(tfidf_matrix)

# === 4. Δημιουργία θεματικών bundles από κάθε cluster ===
cluster_bundles = []

for cluster_id in range(num_clusters):
    cluster_items = product_titles[product_titles['Cluster'] == cluster_id]['Item title'].tolist()

    # Συνδυασμοί 2 προϊόντων ανά cluster
    combos = list(itertools.combinations(cluster_items[:10], 2))  # περιορίζουμε στα 10 για λογικό όγκο
    cluster_bundles.extend(combos)

# === 5. Προβολή ===
print(f"🧠 Thematic Bundles via TF-IDF + KMeans (Clusters: {num_clusters})")
print(f"📦 Συνολικά δημιουργήθηκαν {len(cluster_bundles)} thematic bundles.\n")

# Δείξε τα πρώτα 10
for a, b in cluster_bundles[:10]:
    print(f"👉 {a} + {b}")

# === 6. Μετατροπή σε DataFrame και αποθήκευση ===
thematic_bundle_df = pd.DataFrame(cluster_bundles, columns=['Product A', 'Product B'])

# Προσθήκη Cluster ID για επιπλέον πληροφόρηση (προαιρετικό)
thematic_bundle_df['Cluster'] = None
for cluster_id in range(num_clusters):
    items = product_titles[product_titles['Cluster'] == cluster_id]['Item title'].tolist()
    cluster_combos = list(itertools.combinations(items[:10], 2))
    for combo in cluster_combos:
        thematic_bundle_df.loc[
            (thematic_bundle_df['Product A'] == combo[0]) &
            (thematic_bundle_df['Product B'] == combo[1]), 'Cluster'
        ] = cluster_id

# === Αποθήκευση σε CSV ===
thematic_bundle_df.to_csv("thematic_bundles.csv", index=False)
print("✅ Exported thematic bundles to 'thematic_bundles.csv'")

# === Δημιουργία DataFrame από τα cluster_bundles ===
thematic_bundles_df = pd.DataFrame(cluster_bundles, columns=['Item title A', 'Item title B'])

# Προσθήκη τίτλου και τύπου bundle
thematic_bundles_df['Suggested Bundle Title'] = thematic_bundles_df['Item title A'] + " + " + thematic_bundles_df['Item title B']
thematic_bundles_df['BundleType'] = 'Thematic'

# Έλεγχος
print(f"\n📦 Δημιουργήθηκε thematic_bundles_df με {len(thematic_bundles_df)} γραμμές.")
print(thematic_bundles_df.head())

# === 4.1 Volume Bundles – Εντοπισμός προϊόντων που αγοράζονται σε ποσότητες ===

# Ομαδοποίηση ανά προϊόν: πόσες παραγγελίες, μέσος όρος, μέγιστη ποσότητα
volume_df = orders_df.groupby(['SKU', 'Item title'])['OrderQuantity'].agg(['count', 'mean', 'max']).reset_index()
volume_df.columns = ['SKU', 'Item title', 'Order Count', 'Avg Quantity', 'Max Quantity']

# Επιλογή προϊόντων που έχουν ενδιαφέρον για volume bundles
volume_bundles = volume_df[(volume_df['Avg Quantity'] >= 2) | (volume_df['Max Quantity'] >= 3)].copy()

# === Έξυπνη συνάρτηση για μέγεθος bundle με upper limit ===
def smart_bundle_qty(avg_qty, max_qty=4):
    if avg_qty < 1.8:
        return 2
    elif avg_qty < 2.5:
        return 3
    elif avg_qty < 3.5:
        return 4
    else:
        return min(round(avg_qty), max_qty)

# === Δημιουργία τίτλου προσφοράς χωρίς τιμή ===
def create_bundle_title(row):
    qty = smart_bundle_qty(row['Avg Quantity'])
    return f"{qty}x {row['Item title']} – Offer Pack"

volume_bundles['Suggested Bundle Title'] = volume_bundles.apply(create_bundle_title, axis=1)

# === Προβολή των αποτελεσμάτων ===
print(f"📦 Δημιουργήθηκαν {len(volume_bundles)} Volume Bundles με προτεινόμενους τίτλους:\n")
for i, row in volume_bundles.head(10).iterrows():
    print(f"👉 {row['Suggested Bundle Title']} (Avg: {row['Avg Quantity']:.1f})")

# === Export Volume Bundles to CSV for chatbot ===
volume_bundles_export = volume_bundles[[
    'SKU', 'Item title', 'Order Count', 'Avg Quantity', 'Max Quantity', 'Suggested Bundle Title'
]]

volume_bundles_export.to_csv("volume_bundles.csv", index=False)
print("✅ Exported volume-based bundles to 'volume_bundles.csv'")

# === Μετατροπή volume_bundles σε πλήρες DataFrame για unified pricing ===

# Υπολογισμός ποσότητας bundle (Qty)
volume_bundles['Qty'] = volume_bundles['Avg Quantity'].apply(smart_bundle_qty)

# Προσθήκη τύπου bundle
volume_bundles['BundleType'] = 'Volume'

# Έλεγχος
print(f"\n📦 volume_bundles now ready for pricing with {len(volume_bundles)} bundles.")
print(volume_bundles[['SKU', 'Item title', 'Qty', 'Suggested Bundle Title', 'BundleType']].head())

# === 6.2 Πίνακας με βασικές πληροφορίες ανά προϊόν ===
product_info = orders_df.drop_duplicates(subset='ProductID')[
    ['ProductID', 'Brand', 'Category', 'SKU', 'Item title']
].merge(inventory_df[['SKU', 'Quantity']], on='SKU', how='left')

# === 6.3 Υπολογισμός πωλήσεων ανά ProductID ===
product_sales = orders_df.groupby('ProductID')['OrderNumber'].nunique().reset_index()
product_sales.columns = ['ProductID', 'OrderCount']

# === 6.4 Φιλτράρισμα clearance προϊόντων ===
min_stock = 10
clearance_products = product_sales[
    product_sales['OrderCount'] <= 3
].merge(product_info, on='ProductID')
clearance_products = clearance_products[clearance_products['Quantity'] >= min_stock]

# === 6.5 Επιλογή Top 50 bestsellers ===
top_products = (
    orders_df.groupby('ProductID')['OrderQuantity'].sum()
    .sort_values(ascending=False)
    .head(50)
    .index
)

# === 6.6 Επαναφορά product_info για εύκολη χρήση με index ===
product_info = product_info.set_index('ProductID')

# === 6.7 Δημιουργία bundles: Top-seller + Clearance (Same Brand) ===
bundle_candidates = []

for prod_id in top_products:
    if prod_id not in product_info.index:
        continue  # Skip if missing data
    brand = product_info.loc[prod_id, 'Brand']

    # Clearance του ίδιου brand (όχι το ίδιο προϊόν)
    related_clearance = clearance_products[
        (clearance_products['Brand'] == brand) &
        (clearance_products['ProductID'] != prod_id)
    ]

    for _, row in related_clearance.head(3).iterrows():  # έως 3 ανά bestseller
        bundle_candidates.append((prod_id, row['ProductID']))

# === 6.8 Προβολή αποτελεσμάτων ===
print(f"\n📦 Δημιουργήθηκαν {len(bundle_candidates)} Clearance Bundles (Top-seller + Same Brand with stock ≥ {min_stock}).")
print("🧠 Προτεινόμενα Bundles:")
for a, b in bundle_candidates[:10]:
    title_a = product_info.loc[a, 'Item title']
    title_b = product_info.loc[b, 'Item title']
    print(f"👉 {title_a} + {title_b} (Clearance)")

# === 6.9 Μετατροπή σε DataFrame και αποθήκευση ===
clearance_bundle_rows = []

for a, b in bundle_candidates:
    clearance_bundle_rows.append({
        "Top Seller ID": a,
        "Top Seller Title": product_info.loc[a, 'Item title'],
        "Clearance Product ID": b,
        "Clearance Title": product_info.loc[b, 'Item title'],
        "Brand": product_info.loc[a, 'Brand']
    })

# Convert to DataFrame
clearance_bundle_df = pd.DataFrame(clearance_bundle_rows)

# Save to CSV
clearance_bundle_df.to_csv("clearance_bundles.csv", index=False)
print("✅ Exported clearance bundles to 'clearance_bundles.csv'")

# === Δημιουργία DataFrame για Clearance Bundles ===
clearance_bundles_df = pd.DataFrame(bundle_candidates, columns=['ProductID_A', 'ProductID_B'])

# Επαναχρησιμοποίηση του product_info για τίτλους, SKU, brand
# (έχει ήδη γίνει set_index στο ProductID)

# Merge για πληροφορίες των δύο προϊόντων
clearance_bundles_df = clearance_bundles_df.merge(product_info, left_on='ProductID_A', right_index=True)
clearance_bundles_df = clearance_bundles_df.merge(product_info, left_on='ProductID_B', right_index=True, suffixes=('_A', '_B'))

# Δημιουργία τίτλου bundle και τύπου
clearance_bundles_df['Suggested Bundle Title'] = clearance_bundles_df['Item title_A'] + " + " + clearance_bundles_df['Item title_B']
clearance_bundles_df['BundleType'] = 'Clearance'

# Έλεγχος
print(f"\n📦 Δημιουργήθηκε clearance_bundles_df με {len(clearance_bundles_df)} γραμμές.")
print(clearance_bundles_df.head())



# === 1. Ετοιμασία πηγών τιμής ===
avg_prices = orders_df.groupby('SKU')['FinalUnitPrice'].mean().reset_index()
avg_prices.columns = ['SKU', 'UnitPrice']

# === 2. Volume Pricing ===
volume_pricing = volume_bundles[['SKU', 'Item title', 'Qty', 'Suggested Bundle Title']].copy()
volume_pricing = volume_pricing.merge(avg_prices, on='SKU', how='left')
volume_pricing['FullPrice'] = volume_pricing['Qty'] * volume_pricing['UnitPrice']
# Dynamic discount: more units = more discount, but max at 25%
volume_pricing['DiscountRate'] = volume_pricing['Qty'].apply(
    lambda q: min(0.05 + 0.05 * (q - 2), 0.25)
)

volume_pricing['FinalPrice'] = volume_pricing['FullPrice'] * (1 - volume_pricing['DiscountRate'])
volume_pricing['BundleType'] = 'Volume'

# === 3. Rule-Based Pricing ===
rule_pricing = rule_bundles_df[['SKU_A', 'SKU_B', 'Suggested Bundle Title']].copy()
rule_pricing = rule_pricing.merge(avg_prices, left_on='SKU_A', right_on='SKU', how='left').rename(columns={'UnitPrice': 'Price_A'}).drop('SKU', axis=1)
rule_pricing = rule_pricing.merge(avg_prices, left_on='SKU_B', right_on='SKU', how='left').rename(columns={'UnitPrice': 'Price_B'}).drop('SKU', axis=1)
rule_pricing['FullPrice'] = rule_pricing['Price_A'] + rule_pricing['Price_B']
# Dynamic discount based on number of combined orders of A + B
sku_pair_counts = orders_df.groupby(['OrderNumber'])['SKU'].apply(list)
def pair_order_count(row):
    return sum((row['SKU_A'] in s and row['SKU_B'] in s) for s in sku_pair_counts)

rule_pricing['PairOrderCount'] = rule_pricing.apply(pair_order_count, axis=1)
# Αν το ζεύγος αγοράζεται σπάνια → δώσε μεγαλύτερη έκπτωση για να το προωθήσεις
rule_pricing['DiscountRate'] = rule_pricing['PairOrderCount'].apply(
    lambda c: 0.20 if c < 10 else 0.10 if c < 50 else 0.05
)


rule_pricing['FinalPrice'] = rule_pricing['FullPrice'] * (1 - rule_pricing['DiscountRate'])
rule_pricing['BundleType'] = 'Rule-Based'

# === 4. Clearance Pricing ===
clearance_pricing = clearance_bundles_df[['SKU_A', 'SKU_B', 'Suggested Bundle Title']].copy()
clearance_pricing = clearance_pricing.merge(avg_prices, left_on='SKU_A', right_on='SKU', how='left').rename(columns={'UnitPrice': 'Price_A'}).drop('SKU', axis=1)
clearance_pricing = clearance_pricing.merge(avg_prices, left_on='SKU_B', right_on='SKU', how='left').rename(columns={'UnitPrice': 'Price_B'}).drop('SKU', axis=1)
clearance_pricing['FullPrice'] = clearance_pricing['Price_A'] + clearance_pricing['Price_B']
# Dynamic discount based on inventory levels — higher stock = higher clearance discount
inventory_map = inventory_df.set_index('SKU')['Quantity'].to_dict()

def clearance_discount(row):
    stock_a = inventory_map.get(row['SKU_A'], 0)
    stock_b = inventory_map.get(row['SKU_B'], 0)
    total_stock = stock_a + stock_b
    return 0.15 if total_stock < 20 else 0.25 if total_stock < 50 else 0.35

clearance_pricing['DiscountRate'] = clearance_pricing.apply(clearance_discount, axis=1)

clearance_pricing['FinalPrice'] = clearance_pricing['FullPrice'] * (1 - clearance_pricing['DiscountRate'])
clearance_pricing['BundleType'] = 'Clearance'

# === 5. Thematic Pricing ===
thematic_pricing = thematic_bundles_df[['Item title A', 'Item title B', 'Suggested Bundle Title']].copy()

# Για να βρούμε τιμές, κάνουμε match με orders_df
item_price_map = orders_df.groupby('Item title')['FinalUnitPrice'].mean().to_dict()
thematic_pricing['Price_A'] = thematic_pricing['Item title A'].map(item_price_map)
thematic_pricing['Price_B'] = thematic_pricing['Item title B'].map(item_price_map)
thematic_pricing['FullPrice'] = thematic_pricing['Price_A'] + thematic_pricing['Price_B']
# Dynamic discount based on average price: more expensive bundles = better discount
thematic_pricing['AvgItemPrice'] = (thematic_pricing['Price_A'] + thematic_pricing['Price_B']) / 2
thematic_pricing['DiscountRate'] = thematic_pricing['AvgItemPrice'].apply(
    lambda p: 0.05 if p < 10 else 0.10 if p < 25 else 0.15
)

thematic_pricing['FinalPrice'] = thematic_pricing['FullPrice'] * (1 - thematic_pricing['DiscountRate'])
thematic_pricing['BundleType'] = 'Thematic'

# === 6. Ενοποίηση όλων των bundles ===
all_bundles = pd.concat([
    volume_pricing[['Suggested Bundle Title', 'FullPrice', 'DiscountRate', 'FinalPrice', 'BundleType']],
    rule_pricing[['Suggested Bundle Title', 'FullPrice', 'DiscountRate', 'FinalPrice', 'BundleType']],
    clearance_pricing[['Suggested Bundle Title', 'FullPrice', 'DiscountRate', 'FinalPrice', 'BundleType']],
    thematic_pricing[['Suggested Bundle Title', 'FullPrice', 'DiscountRate', 'FinalPrice', 'BundleType']]
], ignore_index=True)

# Formatting
all_bundles['FinalPrice'] = all_bundles['FinalPrice'].round(2)
all_bundles['OfferLabel'] = all_bundles['DiscountRate'].apply(lambda x: f"-{int(x*100)}%")
all_bundles = all_bundles.sort_values(by='FinalPrice')

# === 7. Προβολή τελικών bundles ===
print(f"✅ Δημιουργήθηκαν συνολικά {len(all_bundles)} bundles με προτεινόμενη τιμή:")
print(all_bundles.head(10))

# === 8. Αποθήκευση όλων των προτάσεων bundle με τιμές ===
all_bundles.to_csv("bundle_prices.csv", index=False)
print("✅ Το αρχείο 'bundle_prices.csv' δημιουργήθηκε επιτυχώς και περιέχει τις τελικές δυναμικές τιμές για όλα τα bundles.")

# === 🔍 Σύγκριση Bundle vs Single Price για Volume Bundles ===

# Αν δεν υπάρχει, υπολόγισε SinglePrice (τιμή 1 τεμαχίου)
if 'SinglePrice' not in volume_pricing.columns:
    volume_pricing['SinglePrice'] = volume_pricing['UnitPrice']

# Αν δεν υπάρχει, δημιούργησε Suggested Bundle Title
if 'Suggested Bundle Title' not in volume_pricing.columns:
    volume_pricing['Suggested Bundle Title'] = volume_pricing['Qty'].astype(str) + 'x Product – Offer Pack'

# Πάρε ένα δείγμα 10 bundles για παρουσίαση
sample = volume_pricing.head(10).copy()

# === 📊 Bar Chart: Bundle vs Single Unit ===
import matplotlib.pyplot as plt

plt.figure(figsize=(25, 15))
bar_width = 0.35
x = range(len(sample))

# Γκρι: 1 τεμάχιο, Πράσινο: Bundle
plt.bar(x, sample['SinglePrice'], width=bar_width, label='Single Unit Price', color='lightgray')
plt.bar([p + bar_width for p in x], sample['FinalPrice'], width=bar_width, label='Bundle Price', color='mediumseagreen')

plt.xticks([p + bar_width / 2 for p in x], sample['Suggested Bundle Title'], rotation=45, ha='right')
plt.ylabel("Price (€)")
plt.title("📦 Bundle vs Single Product Price (Sample)")
plt.legend()
plt.grid(axis='y')
plt.tight_layout()
plt.show()

print("📋 Διαθέσιμες στήλες στο orders_df:")
print(orders_df.columns.tolist())

from datetime import timedelta

# === 1. Προετοιμασία ===
orders_df['CreatedDate'] = pd.to_datetime(orders_df['CreatedDate'], errors='coerce')

# Τελευταίες 30 ημέρες
last_30_days = orders_df[orders_df['CreatedDate'] >= (orders_df['CreatedDate'].max() - timedelta(days=30))]

# Υπολογισμός ημερήσιων πωλήσεων ανά SKU
daily_sales = last_30_days.groupby('SKU')['OrderQuantity'].sum() / 30

# Λεξικό αποθέματος ανά SKU
inventory_lookup = dict(zip(inventory_df['SKU'], inventory_df['Quantity']))

# === 2. Forecast για Volume Bundles ===
volume_forecasts = []

for _, row in volume_pricing.iterrows():
    sku = row['SKU']  # Βεβαιώσου ότι η στήλη λέγεται έτσι
    price = row['FinalPrice']

    # Ημερήσιος ρυθμός πώλησης
    daily_rate = daily_sales.get(sku, 1)

    # Απόθεμα
    stock = inventory_lookup.get(sku, 0)

    # Πόσες μέρες θα κρατήσει το bundle
    duration = int(stock / daily_rate)

    # Προβλεπόμενες πωλήσεις
    expected_sales = int(daily_rate * duration)

    # Προβλεπόμενο έσοδο
    revenue = expected_sales * price

    # Αποθήκευση
    volume_forecasts.append({
        'Bundle Title': row['Suggested Bundle Title'],
        'SKU': sku,
        'FinalPrice (€)': round(price, 2),
        'Duration (days)': duration,
        'Expected Sales': expected_sales,
        'Forecasted Revenue (€)': round(revenue, 2)
    })

# === 3. Τελικός πίνακας ===
volume_forecast_df = pd.DataFrame(volume_forecasts)
volume_forecast_df = volume_forecast_df.sort_values(by='Forecasted Revenue (€)', ascending=False)

# Προβολή
volume_forecast_df.head(10)

# === 4. Αποθήκευση των προβλέψεων για chatbot ===
volume_forecast_df.to_csv("volume_bundle_forecasts.csv", index=False)
print("✅ Το αρχείο 'volume_bundle_forecasts.csv' περιέχει τις προβλέψεις και είναι έτοιμο για χρήση στον chatbot.")

import matplotlib.pyplot as plt

# Top 10 Volume Bundles by revenue
top_volume = volume_forecast_df.head(10)

plt.figure(figsize=(12, 6))
plt.barh(top_volume['Bundle Title'], top_volume['Forecasted Revenue (€)'], color='skyblue')
plt.xlabel('Forecasted Revenue (€)')
plt.title('💰 Top 10 Volume Bundles by Forecasted Revenue')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()



rule_forecasts = []

for _, row in rule_pricing.iterrows():
    sku_a = row['SKU_A']
    sku_b = row['SKU_B']
    price = row['FinalPrice']

    # Daily sales για κάθε SKU
    rate_a = daily_sales.get(sku_a, 1)
    rate_b = daily_sales.get(sku_b, 1)

    # Stock για κάθε SKU
    stock_a = inventory_lookup.get(sku_a, 0)
    stock_b = inventory_lookup.get(sku_b, 0)

    # Διάρκεια (πόσες μέρες αντέχει το bundle)
    duration = int(min(stock_a / rate_a, stock_b / rate_b))

    # Προβλεπόμενες πωλήσεις
    expected_sales = int(min(rate_a * duration, rate_b * duration))

    # Έσοδα
    revenue = expected_sales * price

    rule_forecasts.append({
        'Bundle Title': row['Suggested Bundle Title'],
        'SKU A': sku_a,
        'SKU B': sku_b,
        'FinalPrice (€)': round(price, 2),
        'Duration (days)': duration,
        'Expected Sales': expected_sales,
        'Forecasted Revenue (€)': round(revenue, 2)
    })

# Τελικός πίνακας
rule_forecast_df = pd.DataFrame(rule_forecasts)
rule_forecast_df = rule_forecast_df.sort_values(by='Forecasted Revenue (€)', ascending=False)

# Προβολή
rule_forecast_df.head(10)

# === Αποθήκευση προβλέψεων rule-based bundles ===
rule_forecast_df.to_csv("rule_bundle_forecasts.csv", index=False)
print("✅ Το αρχείο 'rule_bundle_forecasts.csv' δημιουργήθηκε με τις προβλέψεις για rule-based bundles.")

import matplotlib.pyplot as plt

top_rule = rule_forecast_df.head(8)
labels = [f"{a} + {b}" for a, b in zip(top_rule['SKU A'], top_rule['SKU B'])]

plt.figure(figsize=(12, 6))
bars = plt.barh(labels, top_rule['Forecasted Revenue (€)'], color='mediumseagreen')
plt.xlabel('Forecasted Revenue (€)')
plt.title('🔗 Rule-Based Bundles – Forecasted Revenue per Bundle')
plt.gca().invert_yaxis()
plt.grid(axis='x', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()





# === Thematic Bundle Forecast ===

thematic_forecasts = []

for _, row in thematic_pricing.iterrows():
    titles = [row['Item title A'], row['Item title B']]

    # Αντιστοίχιση τίτλων σε SKUs (παίρνει όλα τα SKUs με αυτόν τον τίτλο)
    skus = orders_df[orders_df['Item title'].isin(titles)]['SKU'].unique().tolist()

    # Αν δεν βρούμε 2 SKU, το προσπερνάμε
    if not skus or len(skus) < 2:
        continue

    # Πωλήσεις και απόθεμα για κάθε SKU
    rate_skus = [daily_sales.get(sku, 1) for sku in skus]
    stock_skus = [inventory_lookup.get(sku, 0) for sku in skus]

    # Ελάχιστη διάρκεια (το bottleneck του bundle)
    duration = int(min([stock / rate for stock, rate in zip(stock_skus, rate_skus)]))
    expected_sales = int(min([rate * duration for rate in rate_skus]))
    revenue = row['FinalPrice'] * expected_sales

    thematic_forecasts.append({
        'Bundle Title': row['Suggested Bundle Title'],
        'FinalPrice (€)': round(row['FinalPrice'], 2),
        'Duration (days)': duration,
        'Expected Sales': expected_sales,
        'Forecasted Revenue (€)': round(revenue, 2)
    })

# Τελικός πίνακας
thematic_forecast_df = pd.DataFrame(thematic_forecasts)
thematic_forecast_df = thematic_forecast_df.sort_values(by='Forecasted Revenue (€)', ascending=False)

# Προβολή
print(f"✅ Υπολογίστηκαν προβλέψεις για {len(thematic_forecast_df)} thematic bundles.")
thematic_forecast_df.head(10)

# === Αποθήκευση προβλέψεων thematic bundles ===
thematic_forecast_df.to_csv("thematic_bundle_forecasts.csv", index=False)
print("✅ Το αρχείο 'thematic_bundle_forecasts.csv' δημιουργήθηκε με τις προβλέψεις για thematic bundles.")

import matplotlib.pyplot as plt

# Top 8 thematic bundles by revenue
top_thematic = thematic_forecast_df.head(8)

# Plot
plt.figure(figsize=(12, 8))
plt.barh(top_thematic['Bundle Title'], top_thematic['Forecasted Revenue (€)'], color='darkorange')
plt.xlabel('Forecasted Revenue (€)')
plt.title('🎨 Thematic Bundles – Forecasted Revenue per Bundle')
plt.gca().invert_yaxis()  # Most profitable bundle on top
plt.grid(axis='x', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()

# === Clearance Bundle Forecast ===

clearance_forecasts = []

for _, row in clearance_pricing.iterrows():
    sku_a = row['SKU_A']
    sku_b = row['SKU_B']
    price = row['FinalPrice']

    # Ημερήσιες πωλήσεις (fallback σε 1 εάν λείπει)
    rate_a = daily_sales.get(sku_a, 1)
    rate_b = daily_sales.get(sku_b, 1)

    # Απόθεμα
    stock_a = inventory_lookup.get(sku_a, 0)
    stock_b = inventory_lookup.get(sku_b, 0)

    # Διάρκεια bundle (μέχρι να τελειώσει κάποιο από τα δύο SKUs)
    duration = int(min(stock_a / rate_a, stock_b / rate_b))

    # Εκτιμώμενες πωλήσεις
    expected_sales = int(min(rate_a * duration, rate_b * duration))

    # Προβλεπόμενα έσοδα
    revenue = expected_sales * price

    # Προσθήκη στο τελικό dataframe
    clearance_forecasts.append({
        'Bundle Title': row['Suggested Bundle Title'],
        'SKU A': sku_a,
        'SKU B': sku_b,
        'FinalPrice (€)': round(price, 2),
        'Duration (days)': duration,
        'Expected Sales': expected_sales,
        'Forecasted Revenue (€)': round(revenue, 2)
    })

# Δημιουργία τελικού DataFrame
clearance_forecast_df = pd.DataFrame(clearance_forecasts)
clearance_forecast_df = clearance_forecast_df.sort_values(by='Forecasted Revenue (€)', ascending=False)

# Προβολή
print(f"✅ Υπολογίστηκαν προβλέψεις για {len(clearance_forecast_df)} clearance bundles.")
clearance_forecast_df.head(10)

import matplotlib.pyplot as plt

# 🔟 Πάρε τα top 10 bundles με βάση τα προβλεπόμενα έσοδα
top_clearance = clearance_forecast_df.sort_values(by='Forecasted Revenue (€)', ascending=False).head(10)

# 📊 Δημιουργία διαγράμματος
plt.figure(figsize=(12, 6))
plt.bar(top_clearance['Bundle Title'], top_clearance['Forecasted Revenue (€)'])
plt.title("Top 10 Clearance Bundles by Forecasted Revenue (€)")
plt.xlabel("Bundle Title")
plt.ylabel("Forecasted Revenue (€)")
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()


import pandas as pd

bundle_prices = pd.read_csv("bundle_prices.csv")
volume_forecast_df = pd.read_csv("volume_bundle_forecasts.csv")

print("✅ Φορτώθηκαν τα αρχεία bundle_prices και volume_forecast_df")





print("📦 bundle_prices columns:")
print(bundle_prices.columns.tolist())

print("\n📈 volume_forecast_df columns:")
print(volume_forecast_df.columns.tolist())



# === 📌 TEST CASE: Έλεγχος για Bundles με >15% AOV ===

# Υποθετικό baseline AOV
current_aov = 20
target_aov = current_aov * 1.15

# Merge (προσαρμοσμένο στις σωστές στήλες αν χρειαστεί)
merged_df = pd.merge(
    bundle_prices,
    volume_forecast_df,
    left_on='Suggested Bundle Title',
    right_on='Bundle Title'
)

merged_df['AvgPricePerItem'] = merged_df['FinalPrice'] / 3
aov_bundles = merged_df[
    (merged_df['Duration (days)'] <= 14) &
    (merged_df['AvgPricePerItem'] >= target_aov)
]

# === ✅ Τεστ: υπάρχουν τουλάχιστον 3 bundles που πληρούν το κριτήριο; ===
assert len(aov_bundles) >= 3, "❌ Δεν υπάρχουν αρκετά bundles που αυξάνουν AOV κατά 15%!"

print(f"✅ Βρέθηκαν {len(aov_bundles)} bundles με αύξηση AOV ≥ 15% μέσα σε 14 ημέρες.")

# === 📊 Plot: Top 5 AOV-Boosting Bundles ===
import matplotlib.pyplot as plt

top_plot = aov_bundles.sort_values(by='Forecasted Revenue (€)', ascending=False).head(5)

plt.figure(figsize=(12, 6))
plt.bar(top_plot['Suggested Bundle Title'], top_plot['Forecasted Revenue (€)'])
plt.title("Top 5 Bundles with >15% AOV Boost (Next 2 Weeks)")
plt.ylabel("Forecasted Revenue (€)")
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()


import joblib

# === NLP μοντέλο πρόθεσης ===
vectorizer = joblib.load("intent_vectorizer.joblib")
clf = joblib.load("intent_classifier.joblib")


# === Το μοναδικό endpoint που χρειάζεσαι ===
@app.route("/api/bundles")
def get_bundles():
    sample = all_bundles.sample(n=6, random_state=random.randint(1, 99999))
    print("📤 Bundles sent to frontend:")
    print(sample[['Suggested Bundle Title', 'FinalPrice', 'BundleType']])
    print("➡️ Sending bundles:", sample.head(2).to_dict(orient="records"))
    return jsonify(sample.to_dict(orient="records"))

@app.route("/api/allBundles")
def get_all_bundles():
    print(f"📤 Sending ALL {len(all_bundles)} bundles to frontend...")
    return jsonify(all_bundles.to_dict(orient="records"))

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os
import joblib

app = Flask(__name__)
CORS(app)

# === NLP μοντέλο πρόθεσης ===
vectorizer = joblib.load("intent_vectorizer.joblib")
clf = joblib.load("intent_classifier.joblib")

# === Helper για φόρτωση CSV ===
def load_csv(name):
    return pd.read_csv(os.path.join(os.path.dirname(__file__), name))

@app.route("/api/advisor-data")
def advisor_data():
    from flask import request, jsonify
    import os
    import pandas as pd

    question = request.args.get("question", "").lower().strip()

    # === NLP πρόβλεψη πρόθεσης ===
    X_q = vectorizer.transform([question])
    predicted_intent = clf.predict(X_q)[0]

    # === Keyword overrides ===
    if any(x in question for x in ["forecast", "revenue", "πρόβλεψη", "έσοδο"]):
        predicted_intent = "forecast"
    elif any(x in question for x in ["volume", "multipack", "ποσότητα"]):
        predicted_intent = "volume"
    elif any(x in question for x in ["clear", "απόθεμα", "stock", "ξεπούλημα"]):
        predicted_intent = "clearance"
    elif any(x in question for x in ["theme", "summer", "δώρο", "gift", "season"]):
        predicted_intent = "thematic"
    elif any(x in question for x in ["price", "τιμή", "margin", "discount"]):
        predicted_intent = "price"
    elif any(x in question for x in ["brand", "top seller", "κατηγορία"]):
        predicted_intent = "rule"
    elif any(x in question for x in ["aov", "order value", "καλάθι"]):
        predicted_intent = "aov"

    # === Φόρτωση CSVs ===
    def load_csv(name):
        return pd.read_csv(os.path.join(os.path.dirname(__file__), name))

    inventory = load_csv("data/inventory.csv")
    bundle_prices = load_csv("bundle_prices.csv")
    volume_forecasts = load_csv("volume_bundle_forecasts.csv")
    volume_bundles = load_csv("volume_bundles.csv")
    thematic_bundles = load_csv("thematic_bundles.csv")
    thematic_forecasts = load_csv("thematic_bundle_forecasts.csv")
    rule_forecasts = load_csv("rule_bundle_forecasts.csv")
    top_seller = load_csv("top_seller_bundles.csv")
    clearance = load_csv("clearance_bundles.csv")

    context = f"\n💡 Intent Detected: {predicted_intent}\n"

    # === Επιλογή βάσει intent ===
    if predicted_intent == "aov":
        sample = volume_forecasts.sort_values("Forecasted Revenue (€)", ascending=False).sample(5)
        context += "\n📊 High-AOV Candidates (Sample):\n"
        context += sample[['Bundle Title', 'FinalPrice (€)', 'Forecasted Revenue (€)']].to_string(index=False)

    elif predicted_intent == "price":
        sample = bundle_prices.sort_values("FinalPrice", ascending=False).sample(5)
        context += "\n💰 Price-Focused Bundles (Sample):\n"
        context += sample[['Suggested Bundle Title', 'FullPrice', 'FinalPrice', 'DiscountRate']].to_string(index=False)

    elif predicted_intent == "volume":
        sample = volume_bundles.sample(5)
        context += "\n📦 Volume-Based Bundles:\n"
        context += sample[['Suggested Bundle Title', 'Qty', 'Item title']].to_string(index=False)

    elif predicted_intent == "forecast":
        forecast_df = pd.concat([
            volume_forecasts[['Bundle Title', 'Forecasted Revenue (€)']],
            thematic_forecasts[['Bundle Title', 'Forecasted Revenue (€)']],
            rule_forecasts[['Bundle Title', 'Forecasted Revenue (€)']]
        ])
        sample = forecast_df.sort_values("Forecasted Revenue (€)", ascending=False).sample(6)
        context += "\n📈 Forecasted Revenue – Sample:\n"
        context += sample.to_string(index=False)

    elif predicted_intent == "clearance":
        sample = clearance.sample(min(5, len(clearance)))
        context += "\n🚨 Clearance Bundles:\n"
        context += sample[['Top Seller Title', 'Clearance Title', 'Brand']].to_string(index=False)

    elif predicted_intent == "thematic":
        sample = thematic_bundles.sample(5)
        context += "\n🎨 Thematic Bundles:\n"
        context += sample[['Item title A', 'Item title B', 'Suggested Bundle Title']].to_string(index=False)

    elif predicted_intent == "rule":
        sample = top_seller.sample(5)
        context += "\n📈 Top-Seller Brand Bundles:\n"
        context += sample[['Primary Title', 'Bundled With Title', 'Brand']].to_string(index=False)

    else:
        sample = bundle_prices.sample(5)
        context += "\n🔍 No exact match – here are random bundle suggestions:\n"
        context += sample[['Suggested Bundle Title', 'FinalPrice', 'BundleType']].to_string(index=False)

    print("🧠 Predicted intent:", predicted_intent)
    print("👉 Full question:", question)

    return jsonify({"context": context})


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)