import pandas as pd, numpy as np, re, pickle, warnings, os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    VotingClassifier,
)
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

warnings.filterwarnings("ignore")

# Define paths relative to the script location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "mega_dataset.csv")
CONFIG_PATH = os.path.join(BASE_DIR, "config_data.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "vectorizer.pkl")

print(f"Loading dataset from {DATASET_PATH}...")
data = pd.read_csv(DATASET_PATH)
data.columns = data.columns.str.strip().str.lower()

try:
    if os.path.exists(CONFIG_PATH):
        extra = pd.read_csv(CONFIG_PATH)
        extra.columns = extra.columns.str.strip().str.lower()
        if set(["text", "spam"]).issubset(set(extra.columns)):
            extra = extra[["text", "spam"]].copy()
            extra["spam"] = (
                pd.to_numeric(extra["spam"], errors="coerce").fillna(0).astype(int)
            )
            data = pd.concat([data, extra], ignore_index=True).drop_duplicates(
                subset=["text"]
            )
            print(f"Augmented with {len(extra)} samples from config")
except Exception as e:
    print(f"Skipping config augmentation: {e}")

print(f"Dataset: {data.shape} | {dict(data['spam'].value_counts())}")

# Add cleaning for NaNs before split
data = data.dropna(subset=['text', 'spam'])
X, y = data["text"].astype(str), data["spam"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

def preprocess(t):
    t = str(t).lower()
    t = re.sub(r"https?://\S+|www\.\S+", " urltoken ", t)
    t = re.sub(r"\d+\.\d+\.\d+\.\d+", " iptoken ", t)
    t = re.sub(r"[^\w\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()

print("Preprocessing & vectorizing...")
vectorizer = TfidfVectorizer(
    max_features=12000, # Increased for larger dataset
    ngram_range=(1, 3), 
    min_df=2, 
    max_df=0.9, 
    sublinear_tf=True
)
X_train_v = vectorizer.fit_transform(X_train.apply(preprocess))
X_test_v = vectorizer.transform(X_test.apply(preprocess))

print("Training ensemble (optimized for speed)...")
ensemble = VotingClassifier(
    estimators=[
        (
            "lr",
            LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
        ),
        (
            "rf",
            RandomForestClassifier(
                n_estimators=100, 
                max_depth=15, 
                class_weight="balanced", 
                random_state=42,
                n_jobs=-1
            ),
        ),
        (
            "gb",
            GradientBoostingClassifier(n_estimators=100, max_depth=3, random_state=42),
        ),
    ],
    voting="soft",
)
ensemble.fit(X_train_v, y_train)

print("Evaluating...")
y_pred = ensemble.predict(X_test_v)
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(classification_report(y_test, y_pred, target_names=["SAFE", "PHISHING"]))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

print(f"Saving models to {BASE_DIR}...")
pickle.dump(ensemble, open(MODEL_PATH, "wb"))
pickle.dump(vectorizer, open(VECTORIZER_PATH, "wb"))
print("Model saved successfully!")
