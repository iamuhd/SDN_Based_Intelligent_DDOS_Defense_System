import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

# 1. Load the Data
print("[*] Loading data...")
df = pd.read_csv('traffic_data.csv')

# 2. Prepare Features
X = df[['pkt_rate', 'entropy']]
y = df['label']

# 3. Split Data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Train Model
print("[*] Training the AI model...")
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# 5. Test Model
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

print(f"Model Accuracy: {accuracy * 100:.2f}%")

# --- NEW: GENERATE GRAPH ---
print("[*] Generating Accuracy Graph...")

# Create a Confusion Matrix (The standard accuracy graph)
cm = confusion_matrix(y_test, predictions)

plt.figure(figsize=(8, 6))
# Draw the heatmap
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['Normal', 'Attack'], 
            yticklabels=['Normal', 'Attack'])

plt.xlabel('Predicted Label')
plt.ylabel('Actual Label')
plt.title(f'DDoS Detection Accuracy: {accuracy*100:.2f}%')

# Save the graph as an image file
plt.savefig('accuracy_graph.png')
print("[*] Graph saved as 'accuracy_graph.png'")

# 6. Save the Brain
joblib.dump(model, 'ddos_model.pkl')
