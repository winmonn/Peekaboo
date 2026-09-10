# Peekaboo

A lightweight Python toolkit that finds what is hiding around a domain and takes a peek, built as a learning project on the path to bug bounty hunting.

## What it does

**`recon.py`** — Subdomain discovery via Certificate Transparency logs
- Queries [crt.sh](https://crt.sh) for all certificates ever issued for a given domain
- Parses out unique subdomains, filtering out wildcard entries (`*.example.com`) and email addresses found in certificate data
- Checks liveness of each discovered subdomain via an HTTP request
- Includes retry logic to handle crt.sh's occasional flaky/empty responses
- Outputs three separate files:
  - `active_subdomains.txt` — subdomains that responded to an HTTP request, with status codes
  - `dead_subdomains.txt` — subdomains that didn't respond
  - `emails_found.txt` — email addresses found in certificate records (useful OSINT, kept separate from testable hostnames)

**`probe.py`** — Targeted header/fingerprint inspection
- Takes a small list of specific subdomains (e.g., ones flagged as interesting from `recon.py`'s output)
- Sends a request to each and prints full response headers, one per line
- Useful for comparing security posture across hosts (presence/absence of headers like `Content-Security-Policy`, `Strict-Transport-Security`, `X-Frame-Options`, etc.)

## Setup

```bash
git clone <this-repo-url>
cd Peekaboo
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

## Usage

```bash
python recon.py
# Enter a domain when prompted, e.g. example.com
```

```bash
python probe.py
# Edit the `targets` list inside the script to the specific subdomains you want to inspect
```

## Scope and ethical use

This tool performs **passive reconnaissance only**:
- Certificate Transparency log queries (crt.sh) — public data, no interaction with the target at all
- Basic HTTP GET requests for liveness/header checks — equivalent to visiting a page in a browser

It does **not** perform active testing such as directory brute-forcing, parameter fuzzing, vulnerability scanning, or any form of exploitation.

Only run this against domains you own, or targets where you have explicit authorization (e.g., an enrolled bug bounty program operating within its defined scope). Passive recon of public data is generally low-risk, but you are responsible for confirming what's appropriate for your specific target and program rules.

## Project background

Built incrementally while learning Python and web recon fundamentals — this repo reflects an ongoing bug bounty learning journey rather than a finished, polished product. Future additions may include `robots.txt` / `sitemap.xml` / `security.txt` checking, concurrent request handling, and improved error handling.
