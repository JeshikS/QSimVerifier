import pandas as pd
import os
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

# Load the features
DATA_PATH = os.path.join("data", "processed_features.csv")
data = pd.read_csv(DATA_PATH)

# Basic preprocessing
# Drop non-numeric or identifier columns
X = data.drop(columns=["filename"])

# If label doesn't exist, create dummy labels for demonstration
if "label" not in data.columns:
    print("[INFO] No labels found — creating dummy labels based on filename keywords.")
    def infer_label(filename):
        filename = filename.lower()
        if "vqe" in filename:
            return "vqe"
        elif "qaoa" in filename:
            return "qaoa"
        elif "qft" in filename:
            return "qft"
        elif "ghz" in filename:
            return "ghz"
        elif "dnn" in filename:
            return "dnn"
        elif "knn" in filename:
            return "knn"
        elif "wstate" in filename:
            return "wstate"
        elif "grover" in filename:
            return "grover"
        elif "qpe" in filename:
            return "qpe"
        else:
            return "unknown"

    y = data["filename"].apply(infer_label)
else:
    y = data["label"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train classifier
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Evaluate
y_pred = clf.predict(X_test)
print("Classification Report:")
print(classification_report(y_test, y_pred))
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Save model
MODEL_DIR = "classifiers"
os.makedirs(MODEL_DIR, exist_ok=True)
joblib.dump(clf, os.path.join(MODEL_DIR, "quantum_classifier.pkl"))
print(f"[INFO] Model saved to {os.path.join(MODEL_DIR, 'quantum_classifier.pkl')}")