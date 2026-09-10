import requests

domain = input("Enter a domain to scan: ")
url = f"https://crt.sh/?q=%25.{domain}&output=json"

max_attempts = 3
attempt = 0
data = None

while attempt < max_attempts and data is None:
    attempt += 1
    try:
        response = requests.get(url, timeout=3)
        data = response.json()
    except requests.exceptions.RequestException:
        print(f"Attempt {attempt} failed, retrying...")
    except requests.exceptions.JSONDecodeError:
        print(f"Attempt {attempt} got a bad response, retrying...")

if data is None:
    print("Could not reach crt.sh after multiple attempts. Try again later.")
    exit()

print(f"Got {len(data)} certificate records")

subdomains = set()

for record in data:
    split = record["name_value"].split("\n")
    for parts in split:
        subdomains.add(parts)


print(f"{len(subdomains)} subdomains found")

active_subdomains = open("active_subdomains.txt", "w", encoding="utf-8")
dead_subdomains = open("dead_subdomains.txt", "w", encoding="utf-8")

for domains in sorted(subdomains):
    sub_url = f"https://{domains}"
    try:
        sub_response = requests.get(sub_url, timeout = 5)
        print(f"[ALIVE] {sub_url} - {sub_response.status_code}")
        active_subdomains.write(f"[ALIVE] {sub_url} - Status: {sub_response.status_code}\n")
    except requests.exceptions.RequestException:
        dead_subdomains.write(f"[DEAD] {sub_url}\n")

active_subdomains.close()
dead_subdomains.close()