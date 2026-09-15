import requests
import csv

domain = input("Enter a domain to scan: ")
scope_file_path = input("Enter path to the program's scope CSV: ")

# --- Step 0: Load the official in-scope asset list from the program's CSV ---
scope_allowed = set()

try:
    with open(scope_file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["eligible_for_submission"].strip().lower() == "true":
                scope_allowed.add(row["identifier"].strip())
    print(f"Loaded {len(scope_allowed)} in-scope assets from {scope_file_path}")
except FileNotFoundError:
    print("Scope file not found. Exiting to avoid scanning without a verified scope.")
    exit()

url = f"https://crt.sh/?q=%25.{domain}&output=json"

# --- Step 1: Fetch certificate data from crt.sh, with retries ---
max_attempts = 3
attempt = 0
data = None

while attempt < max_attempts and data is None:
    attempt += 1
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        print(f"Attempt {attempt} succeeded!")
    except requests.exceptions.RequestException:
        print(f"Attempt {attempt} failed (network issue), retrying...")
    except requests.exceptions.JSONDecodeError:
        print(f"Attempt {attempt} got a bad response, retrying...")

if data is None:
    print("Could not reach crt.sh after multiple attempts. Try again later.")
    exit()

print(f"Got {len(data)} certificate records")

# --- Step 2: Extract and categorize subdomains vs emails, skip wildcards ---
subdomains = set()
emails = set()

for record in data:
    split = record["name_value"].split("\n")
    for parts in split:
        if parts.startswith("*"):
            continue
        elif "@" in parts:
            emails.add(parts)
        else:
            subdomains.add(parts)

print(f"{len(subdomains)} subdomains found (before scope filtering)")
print(f"{len(emails)} email addresses found")

# --- Step 2.5: Filter discovered subdomains against the official scope ---
in_scope_subdomains = set()
out_of_scope_count = 0

for sub in subdomains:
    if sub in scope_allowed:
        in_scope_subdomains.add(sub)
    else:
        out_of_scope_count += 1

print(f"{len(in_scope_subdomains)} subdomains are in scope and will be tested")
print(f"{out_of_scope_count} discovered subdomains are NOT in scope and will be skipped")

# --- Step 3: Keywords and status codes that make a result worth flagging ---
interesting_keywords = [
    "admin", "auth", "internal", "upload", "staging", "dashboard",
    "manager", "escalation", "sandbox", "corp", "dev", "test",
    "backup", "api", "login", "vpn", "secret", "config",
    "qa", "uat", "perf", "devint", "stage", "identity", "id",
    "fedsvc", "manage", "portal", "health", "analytics", "people",
    "data", "reports", "dwh", "trafficcop", "cms"
]
interesting_statuses = [401, 403, 502, 503]

# --- Step 4: Liveness check ONLY in-scope subdomains, flag interesting ones ---
active_subdomains = open("active_subdomains.txt", "w", encoding="utf-8")
dead_subdomains = open("dead_subdomains.txt", "w", encoding="utf-8")
email_file = open("emails_found.txt", "w", encoding="utf-8")

for sub in sorted(emails):
    email_file.write(f"{sub}\n")
email_file.close()

worth_noting = []
count = 0

for sub in sorted(in_scope_subdomains):
    sub_url = f"https://{sub}"
    count += 1
    try:
        sub_response = requests.get(sub_url, timeout=5)
        status = sub_response.status_code

        keyword_hit = any(keyword in sub for keyword in interesting_keywords)
        status_hit = status in interesting_statuses
        flagged = keyword_hit or status_hit

        note = " <-- WORTH NOTING" if flagged else ""
        active_subdomains.write(f"[ALIVE] {sub_url} - Status: {status}{note}\n")

        if flagged:
            print(f"[FLAGGED] {sub_url} - Status: {status}{note}")
            reason = []
            if keyword_hit:
                reason.append("keyword match")
            if status_hit:
                reason.append(f"status {status}")
            worth_noting.append((sub_url, status, ", ".join(reason)))
        elif count % 20 == 0:
            print(f"...checked {count}/{len(in_scope_subdomains)} subdomains so far")

    except requests.exceptions.RequestException:
        dead_subdomains.write(f"[DEAD] {sub_url}\n")

active_subdomains.close()
dead_subdomains.close()

# --- Step 5: Save worth-noting hosts to their own file (doubles as probe.py's input) ---
notable_file = open("worth_noting.txt", "w", encoding="utf-8")

print("\n--- Hosts worth noting ---")
if worth_noting:
    for sub_url, status, reason in worth_noting:
        line = f"{sub_url} - Status: {status} - Flagged for: {reason}"
        print(line)
        notable_file.write(line + "\n")
else:
    print("Nothing flagged this run.")

notable_file.close()