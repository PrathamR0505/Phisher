import requests
import json

url = "http://127.0.0.1:5000/check-domain"
res = requests.post(url, json={"domain": "google.com"})
print(res.json())
