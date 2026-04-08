import requests
import json

def test_predict(name, email):
    url = "http://127.0.0.1:5000/predict"
    print(f"\n--- {name} ---")
    try:
        response = requests.post(url, json={"email": email})
        result = response.json()
        print(f"Prediction: {result.get('prediction')}")
        print(f"Risk Score: {result.get('risk_score')}")
        print(f"Reasons: {result.get('reasons')}")
        print(f"Phishing Links Found: {[l['link'] for l in result.get('links', []) if l['status'] == 'PHISHING']}")
        return result
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

# Case 1: High score text (patterns + words + ML) but safe link
# Needs to trigger multiple keywords and patterns
email_high_score_safe_link = """
Subject: Urgent security alert: your bank account was hacked. 
Immediate action required: confirm your identity and verify your bank details now.
Click here to secure your account: https://google.com
"""
test_predict("Test 1 (High Score Text, Safe Link)", email_high_score_safe_link)

# Case 2: Phishing link
email_phishing = "Urgent: Click here to verify http://paypa1-secure.com/verify"
test_predict("Test 2 (Phishing Link)", email_phishing)
