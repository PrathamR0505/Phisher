from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import re, pickle, pandas as pd
from difflib import SequenceMatcher

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


import os

# Define paths relative to the script location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config_data.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "vectorizer.pkl")

def load_config():
    df = pd.read_csv(CONFIG_PATH)
    trusted = set()
    typos = set()
    suspicious_tlds = set()
    brands = []
    words = []
    patterns = []
    for _, r in df.iterrows():
        if r["type"] == "trusted_domain" and r["label"] == "safe":
            trusted.add(r["value"].lower())
        elif r["type"] == "typo_domain":
            typos.add(r["value"].lower())
        elif r["type"] == "suspicious_tld":
            suspicious_tlds.add(r["value"].lower())
        elif r["type"] == "brand_keyword":
            brands.append(r["value"].lower())
        elif r["type"] == "suspicious_word":
            words.append(r["value"].lower())
        elif r["type"] == "phishing_pattern":
            patterns.append(r["value"].lower())
    return {
        "trusted": trusted,
        "typos": typos,
        "suspicious_tlds": suspicious_tlds,
        "brands": brands,
        "words": words,
        "patterns": patterns,
    }

config = load_config()

# Global model/vectorizer cache (optional optimization)
_model = None
_vectorizer = None

def load_ml_model():
    global _model, _vectorizer
    if _model is None or _vectorizer is None:
        _model = pickle.load(open(MODEL_PATH, "rb"))
        _vectorizer = pickle.load(open(VECTORIZER_PATH, "rb"))
    return _model, _vectorizer

def extract_domain(url):
    m = re.findall(r"https?://([^/]+)", url)
    return m[0].lower().replace("www.", "") if m else ""


def get_base(domain):
    parts = domain.split(".")
    return (parts[-2], ".".join(parts[-2:])) if len(parts) >= 2 else (domain, domain)


def normalize(s):
    r = s.lower()
    for n, l in NORM_CHARS.items():
        r = r.replace(n, l)
    return r


def is_typo(base, brands, thresh=0.7):
    base = base.lower()
    for b in brands:
        if base == b:
            continue
        norm_base, norm_brand = normalize(base), normalize(b)
        if norm_base == norm_brand:
            return True, b
        if SequenceMatcher(None, base, b).ratio() >= thresh:
            return True, b
        if SequenceMatcher(None, norm_base, norm_brand).ratio() >= 0.85:
            return True, b
        for i, c in enumerate(base):
            if c.isdigit() and (base[:i] + base[i + 1 :]).startswith(
                b[: len(base) - 1]
            ):
                return True, b
    return False, None


def check_domain(domain):
    domain = domain.lower().strip()
    if domain in config["trusted"]:
        return "SAFE"
    base, full = get_base(domain)
    for t in config["trusted"]:
        if get_base(t)[0] == base:
            return "SAFE"
            
    # Subdomain spoofing detection (e.g., paypal.secure-login.com)
    for b in config["brands"]:
        if b in domain and b != base:
            return "PHISHING"
    
    typo, brand = is_typo(base, config["brands"], 0.65)
    if typo:
        return "PHISHING"
    for t in config["typos"]:
        if get_base(t)[0] in base or base in get_base(t)[0]:
            return "PHISHING"
    for tld in config["suspicious_tlds"]:
        if full.endswith(tld):
            return "PHISHING"
    if re.match(r"\d+\.\d+\.\d+\.\d+", domain):
        return "PHISHING"
    if (
        re.match(
            r"^[^a-z]*$|^[a-z]+[0-9]+[a-z]*$|[a-z]([a-z])\1{2,}|^[^aeiou]{4,}$", base
        )
        and len(base) >= 4
    ):
        return "PHISHING"
    for b in config["brands"]:
        if b in base and base != b:
            return "PHISHING"
    return "SUSPICIOUS"


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
