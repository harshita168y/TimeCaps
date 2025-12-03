import requests
BASE_URL = "http://10.10.14.25:8000"
day = "2025-11-30"
resp = requests.post(
    f"{BASE_URL}/generate_wrapup",
    params={"force": "true", "day": day}, 
)
print(resp.status_code, resp.json())
