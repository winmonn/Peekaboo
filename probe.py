import requests

# --- Step 1: Choose target(s) - single manual URL, or the full worth_noting.txt list ---
choice = input("Probe a single URL, or all hosts in worth_noting.txt? (single/all): ").strip().lower()

targets = []

if choice == "single":
    manual_url = input("Enter the full URL (e.g. https://example.example.com): ").strip()
    targets.append(manual_url)
else:
    try:
        with open("worth_noting.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                url = line.split(" - ")[0]
                targets.append(url)
    except FileNotFoundError:
        print("worth_noting.txt not found. Run recon.py first to generate it.")
        exit()

if not targets:
    print("No targets to probe.")
    exit()

print(f"Probing {len(targets)} target(s)\n")

# --- Step 2: Probe each target, save full response headers to file ---
output_file = open("probe_results.txt", "w", encoding="utf-8")

for url in targets:
    try:
        response = requests.get(url, timeout=5)
        line = f"[ACTIVE] {url} - Status: {response.status_code}"
        output_file.write(line + "\n")

        for key, value in response.headers.items():
            header_line = f"  {key}: {value}"
            output_file.write(header_line + "\n")

        output_file.write("-" * 40 + "\n")

    except requests.exceptions.RequestException:
        line = f"[UNREACHABLE] {url}"
        output_file.write(line + "\n")
        output_file.write("-" * 40 + "\n")

output_file.close()
print(f"Done. Results saved to probe_results.txt")