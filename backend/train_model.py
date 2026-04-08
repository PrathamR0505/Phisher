import pandas as pd, numpy as np, re, pickle, warnings
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

print("Loading dataset...")
data = pd.read_csv("dataset.csv")
data.columns = data.columns.str.strip().str.lower()

try:
    extra = pd.read_csv("config_data.csv")
    extra.columns = extra.columns.str.strip().str.lower()
    if set(["text", "spam"]).issubset(set(extra.columns)):
        extra = extra[["text", "spam"]].copy()
        extra["spam"] = (
            pd.to_numeric(extra["spam"], errors="coerce").fillna(0).astype(int)
        )
        data = pd.concat([data, extra], ignore_index=True).drop_duplicates(
            subset=["text"]
        )
        print(f"Augmented with {len(extra)} samples")
except:
    print("Skipping config augmentation")

print(f"Dataset: {data.shape} | {dict(data['spam'].value_counts())}")

X, y = data["text"].astype(str), data["spam"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)


def preprocess(t):
    t = str(t).lower()
    t = re.sub(r"http\S+|www\.\S+", " urltoken ", t)
    t = re.sub(r"\d+\.\d+\.\d+\.\d+", " iptoken ", t)
    t = re.sub(r"[^\w\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


print("Preprocessing & vectorizing...")
vectorizer = TfidfVectorizer(
    max_features=8000, ngram_range=(1, 3), min_df=1, max_df=0.95, sublinear_tf=True
)
X_train_v = vectorizer.fit_transform(X_train.apply(preprocess))
X_test_v = vectorizer.transform(X_test.apply(preprocess))

print("Training ensemble...")
ensemble = VotingClassifier(
    estimators=[
        (
            "lr",
            LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
        ),
        (
            "rf",
            RandomForestClassifier(
                n_estimators=200, max_depth=20, class_weight="balanced", random_state=42
            ),
        ),
        (
            "gb",
            GradientBoostingClassifier(n_estimators=150, max_depth=5, random_state=42),
        ),
    ],
    voting="soft",
)
ensemble.fit(X_train_v, y_train)

print("Evaluating...")
y_pred = ensemble.predict(X_test_v)
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(f"CV Score: {cross_val_score(ensemble, X_train_v, y_train, cv=5).mean():.4f}")
print(classification_report(y_test, y_pred, target_names=["SAFE", "PHISHING"]))
print("Confusion Matrix:", confusion_matrix(y_test, y_pred))

pickle.dump(ensemble, open("model.pkl", "wb"))
pickle.dump(vectorizer.fit(X.apply(preprocess)), open("vectorizer.pkl", "wb"))
print("Model saved!")
