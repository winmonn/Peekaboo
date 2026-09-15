import requests

target_domain = input("Enter the domain you're checking for redirects to (e.g. example.example.com): ").strip()

targets = []
with open("active_subdomains.txt", "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("[ALIVE]"):
            url = line.split(" ")[1]
            targets.append(url)

for url in targets:
    try:
        response = requests.get(url, timeout=5, allow_redirects=True)
        final_url = response.url
        if target_domain in final_url and url != final_url.rstrip("/"):
            print(f"FOUND: {url} --> {final_url}")
    except requests.exceptions.RequestException:
        pass