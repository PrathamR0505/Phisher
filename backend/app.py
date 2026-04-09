from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import re
import pickle
import pandas as pd
from difflib import SequenceMatcher
from typing import List, Dict, Any, Tuple, Optional
import os
import shutil
import pdfplumber
import pytesseract
from PIL import Image

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

allowed_origins = [
    origin.strip()
    for origin in os.environ.get("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if origin.strip()
]

CORS(app, resources={r"/*": {
    "origins": allowed_origins,
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

def configure_tesseract() -> Optional[str]:
    env_path = os.environ.get("TESSERACT_CMD", "").strip()
    if env_path and os.path.exists(env_path):
        pytesseract.pytesseract.tesseract_cmd = env_path
        return env_path

    windows_default = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(windows_default):
        pytesseract.pytesseract.tesseract_cmd = windows_default
        return windows_default

    path_binary = shutil.which("tesseract")
    if path_binary:
        pytesseract.pytesseract.tesseract_cmd = path_binary
        return path_binary

    import glob

    for path_glob in ["/usr/bin/tesseract", "/usr/local/bin/tesseract", "/nix/store/*/bin/tesseract"]:
        matches = glob.glob(path_glob)
        if matches:
            pytesseract.pytesseract.tesseract_cmd = matches[0]
            return matches[0]

    return None

TESSERACT_CMD = configure_tesseract()

def ensure_tesseract_available() -> None:
    try:
        pytesseract.get_tesseract_version()
    except Exception as exc:
        configured_path = getattr(pytesseract.pytesseract, "tesseract_cmd", "tesseract")
        raise RuntimeError(
            "Tesseract OCR is not available on the server. "
            f"Configured command: '{configured_path}'. "
            "On Render, install it via nixpacks and redeploy."
        ) from exc

NORM_CHARS = {
    "0": "o", "1": "l", "3": "e", "4": "a", "5": "s", "7": "t", "8": "b", "9": "g", "$": "s", "@": "a", "6": "g", "2": "z",
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config_data.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "vectorizer.pkl")

def load_config() -> Dict[str, Any]:
    try:
        df = pd.read_csv(CONFIG_PATH)
        trusted, typos, suspicious_tlds = set(), set(), set()
        brands, words, patterns = [], [], []
        for _, r in df.iterrows():
            t = r["type"]
            v = str(r["value"]).lower()
            if t == "trusted_domain" and r["label"] == "safe":
                trusted.add(v)
            elif t == "typo_domain":
                typos.add(v)
            elif t == "suspicious_tld":
                suspicious_tlds.add(v)
            elif t == "brand_keyword":
                brands.append(v)
            elif t == "suspicious_word":
                words.append(v)
            elif t == "phishing_pattern":
                patterns.append(v)
        return {"trusted": trusted, "typos": typos, "suspicious_tlds": suspicious_tlds, "brands": brands, "words": words, "patterns": patterns}
    except Exception as e:
        print(f"Error loading config: {e}")
        return {"trusted": set(), "typos": set(), "suspicious_tlds": set(), "brands": [], "words": [], "patterns": []}

config = load_config()
_model, _vectorizer = None, None

def load_ml_model():
    global _model, _vectorizer
    if _model is None or _vectorizer is None:
        if not os.path.exists(MODEL_PATH) or not os.path.exists(VECTORIZER_PATH):
            raise FileNotFoundError("Model files not found")
        with open(MODEL_PATH, "rb") as f:
            _model = pickle.load(f)
        with open(VECTORIZER_PATH, "rb") as f:
            _vectorizer = pickle.load(f)
    return _model, _vectorizer

def extract_domain(url):
    m = re.findall(r"https?://([^/]+)", url)
    return m[0].lower().replace("www.", "") if m else ""

def get_base(domain_str: str) -> Tuple[str, str]:
    domain_parts: List[str] = domain_str.split(".")
    if len(domain_parts) >= 2:
        # Use simple indexing to avoid linter confusion with slices
        tld = domain_parts[len(domain_parts)-1]
        base = domain_parts[len(domain_parts)-2]
        return (base, f"{base}.{tld}")
    return (domain_str, domain_str)

def normalize(s):
    r = s.lower()
    for num, char in NORM_CHARS.items():
        r = r.replace(num, char)
    return r

def is_typo(target_str: str, brands_list: List[str], thresh: float = 0.7) -> Tuple[bool, Optional[str]]:
    target_str = target_str.lower()
    for b in brands_list:
        if target_str == b:
            continue
        norm_target, norm_brand = normalize(target_str), normalize(b)
        if norm_target == norm_brand or SequenceMatcher(None, target_str, b).ratio() >= thresh or SequenceMatcher(None, norm_target, norm_brand).ratio() >= 0.85:
            return True, b
        for i in range(len(target_str)):
            c = target_str[i]
            if c.isdigit():
                # Avoid direct slice in loop if possible, or use explicit indexing
                prefix = target_str[0:i]
                suffix = target_str[i+1:]
                combined = prefix + suffix
                if combined.startswith(b[:len(target_str) - 1]):
                    return True, b
    return False, None

def check_domain(domain: str) -> str:
    domain = domain.lower().strip()
    if domain in config["trusted"]:
        return "SAFE"
    base_domain, full_domain = get_base(domain)
    for t in config["trusted"]:
        trusted_base, _ = get_base(str(t))
        if trusted_base == base_domain:
            return "SAFE"
    for b in config["brands"]:
        if b in domain and b != base_domain:
            return "PHISHING"
    typo, _ = is_typo(base_domain, config["brands"], 0.65)
    if typo:
        return "PHISHING"
    for t in config["typos"]:
        if get_base(t)[0] in base_domain or base_domain in get_base(t)[0]:
            return "PHISHING"
    for tld in config["suspicious_tlds"]:
        if full_domain.endswith(tld):
            return "PHISHING"
    if re.match(r"\d+\.\d+\.\d+\.\d+", domain):
        return "PHISHING"
    if re.match(r"^[^a-z]*$|^[a-z]+[0-9]+[a-z]*$|[a-z]([a-z])\1{2,}|^[^aeiou]{4,}$", base_domain) and len(base_domain) >= 4:
        return "PHISHING"
    return "SUSPICIOUS"

def check_link(text):
    results = []
    for link_str in re.findall(r"(https?://\S+)", text, re.I):
        d = extract_domain(link_str)
        status = check_domain(d) if d else "PHISHING"
        results.append({"link": link_str, "domain": d, "status": status})
    return results

def analyze_text(text: str) -> Dict[str, Any]:
    try:
        model, vectorizer = load_ml_model()
        ml_available = True
    except Exception:
        ml_available = False

    text = text.lower()
    score = 0
    reasons = []
    links = check_link(text)
    phishing_links = [link_item for link_item in links if link_item["status"] == "PHISHING"]
    suspicious_links = [link_item for link_item in links if link_item["status"] == "SUSPICIOUS"]

    if phishing_links:
        score += 70
        reasons.extend([f"Phishing domain: '{link_item['domain']}'" for link_item in phishing_links])
    if suspicious_links:
        score += 40
        reasons.extend([f"Suspicious domain: '{link_item['domain']}'" for link_item in suspicious_links])
    
    has_ip_link = bool(re.findall(r"https?://\d+\.\d+\.\d+\.\d+", text))
    if has_ip_link:
        score += 85
        reasons.append("High-risk IP address link detected")

    critical_words = {"urgent", "suspended", "unauthorized", "immediately", "compromised", "hacked", "stolen", "fraud", "scam"}
    action_words = {"verify", "confirm", "update", "security", "alert", "locked", "expire", "action", "required"}
    sensitive_targets = {"bank", "account", "login", "password", "wallet", "crypto", "bitcoin"}
    
    email_words = set(re.findall(r"\b\w+\b", text))
    found_critical = email_words.intersection(critical_words)
    found_action = email_words.intersection(action_words)
    found_sensitive = email_words.intersection(sensitive_targets)
    
    score += len(found_critical) * 15 + len(found_action) * 10 + len(found_sensitive) * 5
    if found_critical:
        reasons.append(f"Critical indicators: {', '.join(found_critical)}")
    if found_action:
        reasons.append(f"Action requested: {', '.join(found_action)}")
    if found_critical and found_action:
        score += 15
        reasons.append("Pattern: Urgency with required action")
    if found_action and found_sensitive:
        score += 10
        reasons.append("Pattern: Action requested on sensitive account")
    if any(p in text for p in config["patterns"]):
        score += 35
        reasons.append("Contains known phishing message patterns")

    for link_item in links:
        if link_item["domain"]:
            b, _ = get_base(link_item["domain"])
            t, brand = is_typo(b, config["brands"])
            if t:
                score += 25
                reasons.append(f"Link typo detection: '{b}' mimics '{brand}'")
            if link_item["status"] == "PHISHING":
                score += 90

    if ml_available:
        try:
            pred = model.predict(vectorizer.transform([text]))[0]
            prob = model.predict_proba(vectorizer.transform([text]))[0]
            if pred == 1:
                score += 30
                reasons.append("ML model identified phishing characteristics")
            ml_result = {
                "prediction": "PHISHING" if pred == 1 else "SAFE",
                "confidence": round(max(prob) * 100, 2)
            }
        except Exception:
            ml_result = {"error": "ML analysis failed"}
    else:
        ml_result = {"available": False}

    score = min(score, 100)
    prediction = "PHISHING" if score >= 80 else "SUSPICIOUS" if score >= 45 else "SAFE"
    if prediction == "PHISHING" and not (any(link_item["status"] == "PHISHING" for link_item in links) or has_ip_link):
        prediction = "SUSPICIOUS"

    return {"prediction": prediction, "risk_score": score, "reasons": reasons, "links": links, "ml_analysis": ml_result}

@app.route("/health")
def health_check():
    return jsonify({"status": "healthy", "service": "phishing-detector-api"}), 200

@app.route("/api")
def api_home():
    return jsonify({
        "status": "Backend API is running",
        "endpoints": ["/api/predict", "/api/predict-file", "/api/check-domain", "/api/reload-config", "/health"]
    })

@app.route("/predict", methods=["POST"])
def predict():
    email = request.json.get("email", "")
    if not email:
        return jsonify({"error": "No email content provided"}), 400
    return jsonify(analyze_text(email))

@app.route("/predict-file", methods=["POST"])
def predict_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    extracted_text = ""
    filename = file.filename.lower()
    try:
        if filename.endswith('.pdf'):
            with pdfplumber.open(file) as pdf:
                extracted_text = " ".join([page.extract_text() or "" for page in pdf.pages])
        elif filename.endswith(('.png', '.jpg', '.jpeg', '.webp')):
            ensure_tesseract_available()
            img = Image.open(file.stream)
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")
            extracted_text = pytesseract.image_to_string(img)
        else:
            return jsonify({"error": "Unsupported file type"}), 400
        if not extracted_text.strip():
            return jsonify({"error": "No text could be extracted from the file"}), 400
        return jsonify(analyze_text(extracted_text))
    except Exception as e:
        print(f"Error processing file: {e}")
        return jsonify({"error": f"Error processing file: {str(e)}"}), 500

@app.errorhandler(413)
def file_too_large(_error):
    return jsonify({"error": "File is too large. Please upload a file smaller than 10 MB."}), 413

@app.route("/check-domain", methods=["POST"])
def check_domain_api():
    domain = request.json.get("domain", "").lower()
    if not domain:
        return jsonify({"domain": "unknown", "status": "PHISHING", "reason": "No domain"})
    status = check_domain(domain)
    base, _ = get_base(domain)
    typo, brand = is_typo(base, config["brands"])
    reason = "Domain is trusted" if status == "SAFE" else (
        f"Typo of '{brand}'" if typo else
        "Suspicious domain" if status == "SUSPICIOUS" else
        "Phishing domain"
    )
    return jsonify({"domain": domain, "status": status, "base_domain": base, "reason": reason})

@app.route("/reload-config", methods=["POST"])
def reload():
    global config
    config = load_config()
    return jsonify({"status": "success", "stats": {k: len(v) if isinstance(v, (set, list)) else 0 for k, v in config.items()}})

if __name__ == "__main__":
    print(f"Trusted: {len(config['trusted'])}, Typos: {len(config['typos'])}, TLDs: {len(config['suspicious_tlds'])}")
    # Disabled reloader to prevent infinite loops on some Windows environments
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)), host="0.0.0.0", use_reloader=False)
