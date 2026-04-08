from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import re, pickle, pandas as pd
from difflib import SequenceMatcher
from typing import Set, List, Dict, Any, Tuple, Optional

app = Flask(__name__)
CORS(app)

NORM_CHARS = {
    "0": "o",
    "1": "l",
    "3": "e",
    "4": "a",
    "5": "s",
    "7": "t",
    "8": "b",
    "9": "g",
    "$": "s",
    "@": "a",
    "6": "g",
    "2": "z",
}
# Initialize CORS with more explicit settings
CORS(app, resources={r"/*": {"origins": "*"}})

import os

# Define paths relative to the script location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config_data.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "vectorizer.pkl")

def load_config() -> Dict[str, Any]:
    try:
        df = pd.read_csv(CONFIG_PATH)
        trusted: Set[str] = set()
        typos: Set[str] = set()
        suspicious_tlds: Set[str] = set()
        brands: List[str] = []
        words: List[str] = []
        patterns: List[str] = []
        for _, r in df.iterrows():
            if r["type"] == "trusted_domain" and r["label"] == "safe":
                trusted.add(str(r["value"]).lower())
            elif r["type"] == "typo_domain":
                typos.add(str(r["value"]).lower())
            elif r["type"] == "suspicious_tld":
                suspicious_tlds.add(str(r["value"]).lower())
            elif r["type"] == "brand_keyword":
                brands.append(str(r["value"]).lower())
            elif r["type"] == "suspicious_word":
                words.append(str(r["value"]).lower())
            elif r["type"] == "phishing_pattern":
                patterns.append(str(r["value"]).lower())
        return {
            "trusted": trusted,
            "typos": typos,
            "suspicious_tlds": suspicious_tlds,
            "brands": brands,
            "words": words,
            "patterns": patterns,
        }
    except Exception as e:
        print(f"Error loading config: {e}")
        return {"trusted": set(), "typos": set(), "suspicious_tlds": set(), "brands": [], "words": [], "patterns": []}

config = load_config()

# Global model/vectorizer cache
_model = None
_vectorizer = None

def load_ml_model():
    global _model, _vectorizer
    if _model is None or _vectorizer is None:
        if not os.path.exists(MODEL_PATH) or not os.path.exists(VECTORIZER_PATH):
            raise FileNotFoundError("Model files not found")
        _model = pickle.load(open(MODEL_PATH, "rb"))
        _vectorizer = pickle.load(open(VECTORIZER_PATH, "rb"))
    return _model, _vectorizer

def extract_domain(url):
    m = re.findall(r"https?://([^/]+)", url)
    return m[0].lower().replace("www.", "") if m else ""


def get_base(domain_str: str) -> Tuple[str, str]:
    parts = domain_str.split(".")
    if len(parts) >= 2:
        # Use explicit list slicing and joining
        last_two = parts[-2:]
        return (str(parts[-2]), ".".join(last_two))
    return (domain_str, domain_str)


def normalize(s):
    r = s.lower()
    for n, l in NORM_CHARS.items():
        r = r.replace(n, l)
    return r


def is_typo(target_str: str, brands_list: List[str], thresh: float = 0.7) -> Tuple[bool, Optional[str]]:
    target_str = target_str.lower()
    for b in brands_list:
        if target_str == b:
            continue
        norm_target, norm_brand = normalize(target_str), normalize(b)
        if norm_target == norm_brand:
            return True, b
        if SequenceMatcher(None, target_str, b).ratio() >= thresh:
            return True, b
        if SequenceMatcher(None, norm_target, norm_brand).ratio() >= 0.85:
            return True, b
            
        # Refactored for better type inference and to avoid name collisions
        for i, c in enumerate(target_str):
            if c.isdigit():
                prefix: str = target_str[:i]
                suffix: str = target_str[i + 1:]
                modified_str = prefix + suffix
                brand_prefix: str = b[:len(target_str) - 1]
                if modified_str.startswith(brand_prefix):
                    return True, b
    return False, None


def check_domain(domain: str) -> str:
    domain = domain.lower().strip()
    trusted_set: Set[str] = config["trusted"]
    if domain in trusted_set:
        return "SAFE"
    
    base_domain, full_domain = get_base(domain)
    for t in trusted_set:
        if get_base(t)[0] == base_domain:
            return "SAFE"
            
    # Subdomain spoofing detection (e.g., paypal.secure-login.com)
    brands_list: List[str] = config["brands"]
    for b in brands_list:
        if b in domain and b != base_domain:
            return "PHISHING"
    
    typo, _ = is_typo(base_domain, brands_list, 0.65)
    if typo:
        return "PHISHING"
    
    typos_set: Set[str] = config["typos"]
    for t in typos_set:
        t_base, _ = get_base(t)
        if t_base in base_domain or base_domain in t_base:
            return "PHISHING"
            
    suspicious_tlds: Set[str] = config["suspicious_tlds"]
    for tld in suspicious_tlds:
        if full_domain.endswith(tld):
            return "PHISHING"
    
    if re.match(r"\d+\.\d+\.\d+\.\d+", domain):
        return "PHISHING"
        
    if (
        re.match(
            r"^[^a-z]*$|^[a-z]+[0-9]+[a-z]*$|[a-z]([a-z])\1{2,}|^[^aeiou]{4,}$", base_domain
        )
        and len(base_domain) >= 4
    ):
        return "PHISHING"
    return "UNKNOWN"


def check_link(text):
    return [
        {
            "link": l,
            "domain": extract_domain(l),
            "status": check_domain(extract_domain(l))
            if extract_domain(l)
            else "PHISHING",
        }
        for l in re.findall(r"(https?://\S+)", text, re.I)
    ]


def count_suspicious(text):
    words = re.findall(r"\b\w+\b", text.lower())
    found = [w for w in words if w in config["words"]]
    return len(found), found

@app.route("/")
def home():
    return jsonify({"status": "Backend is running", "endpoints": ["/predict", "/check-domain", "/reload-config"]})


@app.route("/predict", methods=["POST"])
def predict():
    try:
        model, vectorizer = load_ml_model()
        ml_available = True
    except:
        ml_available = False

    email = request.json.get("email", "").lower()
    score = 0
    reasons = []
    links = check_link(email)
    phishing_links = [l for l in links if l["status"] == "PHISHING"]
    suspicious_links = [l for l in links if l["status"] == "SUSPICIOUS"]

    if phishing_links:
        score += 70
        reasons.extend([f"Phishing domain: '{l['domain']}'" for l in phishing_links])
    if suspicious_links:
        score += 40
        reasons.extend(
            [f"Suspicious domain: '{l['domain']}'" for l in suspicious_links]
        )
    has_ip_link = bool(re.findall(r"https?://\d+\.\d+\.\d+\.\d+", email))
    if has_ip_link:
        score += 85
        reasons.append("High-risk IP address link detected")

    # Granular Weighted Word Scoring
    critical_words = {"urgent", "suspended", "unauthorized", "immediately", "compromised", "hacked", "stolen", "fraud", "scam"}
    action_words = {"verify", "confirm", "update", "security", "alert", "locked", "expire", "action", "required"}
    sensitive_targets = {"bank", "account", "login", "password", "wallet", "crypto", "bitcoin"}
    
    email_words = set(re.findall(r"\b\w+\b", email.lower()))
    found_critical = email_words.intersection(critical_words)
    found_action = email_words.intersection(action_words)
    found_sensitive = email_words.intersection(sensitive_targets)
    
    score += len(found_critical) * 15
    score += len(found_action) * 10
    score += len(found_sensitive) * 5
    
    if found_critical:
        reasons.append(f"Critical indicators: {', '.join(found_critical)}")
    if found_action:
        reasons.append(f"Action requested: {', '.join(found_action)}")
        
    # Co-occurrence bonuses (Pattern Heuristics)
    if found_critical and found_action:
        score += 15
        reasons.append("Pattern: Urgency with required action")
    if found_action and found_sensitive:
        score += 10
        reasons.append("Pattern: Action requested on sensitive account")

    if any(p in email for p in config["patterns"]):
        score += 35
        reasons.append("Contains known phishing message patterns")

    for l in links:
        if l["domain"]:
            b, _ = get_base(l["domain"])
            t, brand = is_typo(b, config["brands"])
            if t:
                score += 25
                reasons.append(f"Link typo detection: '{b}' mimics '{brand}'")
            if l["status"] == "PHISHING":
                score += 90

    if ml_available:
        try:
            pred = model.predict(vectorizer.transform([email]))[0]
            prob = model.predict_proba(vectorizer.transform([email]))[0]
            if pred == 1:
                score += 30
                reasons.append("ML model identified phishing characteristics")
            ml_result = {
                "prediction": "PHISHING" if pred == 1 else "SAFE",
                "confidence": round(max(prob) * 100, 2),
            }
        except:
            ml_result = {"error": "ML analysis failed"}
    else:
        ml_result = {"available": False}

    score = min(score, 100)
    prediction = "PHISHING" if score >= 80 else "SUSPICIOUS" if score >= 45 else "SAFE"

    # Secondary classification check
    has_high_risk_indicator = any(l["status"] == "PHISHING" for l in links) or has_ip_link
    if prediction == "PHISHING" and not has_high_risk_indicator:
        prediction = "SUSPICIOUS"



    return jsonify(
        {
            "prediction": prediction,
            "risk_score": score,
            "reasons": reasons,
            "links": links,
            "ml_analysis": ml_result,
        }
    )


@app.route("/check-domain", methods=["POST"])
def check_domain_api():
    domain = request.json.get("domain", "").lower()
    if not domain:
        return jsonify(
            {"domain": "unknown", "status": "PHISHING", "reason": "No domain"}
        )
    status = check_domain(domain)
    base, _ = get_base(domain)
    typo, brand = is_typo(base, config["brands"])
    reason = (
        "Domain is trusted"
        if status == "SAFE"
        else (
            f"Typo of '{brand}'"
            if typo
            else "Suspicious domain"
            if status == "SUSPICIOUS"
            else "Phishing domain"
        )
    )
    return jsonify(
        {"domain": domain, "status": status, "base_domain": base, "reason": reason}
    )


@app.route("/reload-config", methods=["POST"])
def reload():
    global config
    config = load_config()
    return jsonify(
        {
            "status": "success",
            "stats": {
                k: len(v) if isinstance(v, (set, list)) else 0
                for k, v in config.items()
            },
        }
    )


if __name__ == "__main__":
    print(
        f"Trusted: {len(config['trusted'])}, Typos: {len(config['typos'])}, TLDs: {len(config['suspicious_tlds'])}"
    )
    app.run(debug=True, port=5000, host="0.0.0.0")
