import requests

targets = ["login.corp.google.com", "sandbox.google.com", "wifi.google.com"]

for subdomains in targets:
    url = f"https://{subdomains}"
    try:
        response = requests.get(url, timeout=5)
        print(f"[ACTIVE] {url} - Status: {response.status_code}")
        for key, value in response.headers.items():
            print(f"{key}: {value}")
        print("-" * 40)
    except requests.exceptions.RequestException:
        print(f"[UNREACHABLE] {url}")