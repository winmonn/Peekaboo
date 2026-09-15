# Peekaboo

A lightweight Python toolkit for passive subdomain reconnaissance, built as a learning project on the path to bug bounty hunting.

## What it does

**`recon.py`** — Scope-aware subdomain discovery via Certificate Transparency logs
- Queries [crt.sh](https://crt.sh) for all certificates ever issued for a given domain, with retry logic to handle crt.sh's occasional flaky/empty responses
- Parses out unique subdomains, filtering out wildcard entries (`*.example.com`) and separating out email addresses found in certificate data
- Cross-references discovered subdomains against a bug bounty program's official scope CSV (exported from HackerOne), so only explicitly authorized assets are ever tested — anything not in scope is skipped entirely, never touched
- Checks liveness of each in-scope subdomain via an HTTP request
- Flags results "worth noting" based on configurable keyword matches (e.g. `admin`, `staging`, `internal`) and interesting HTTP status codes (401, 403, 502, 503) — surfacing likely-interesting hosts automatically instead of requiring a manual read-through of hundreds of results
- Outputs four separate files:
  - `active_subdomains.txt` — in-scope subdomains that responded, with status codes and flagging notes
  - `dead_subdomains.txt` — in-scope subdomains that didn't respond
  - `emails_found.txt` — email addresses found in certificate records (useful OSINT, kept separate from testable hostnames)
  - `worth_noting.txt` — just the flagged hosts and why they were flagged; doubles as the input list for `probe.py`

**`probe.py`** — Targeted header/fingerprint inspection
- Probes either a single manually-entered URL, or every host listed in `worth_noting.txt`
- Sends a request to each target and saves full response headers to `probe_results.txt`
- Useful for comparing security posture across hosts (presence/absence of headers like `Content-Security-Policy`, `Strict-Transport-Security`, `X-Frame-Options`, WAF fingerprints, etc.)

**`trace.py`** — SSO/redirect relationship mapper
- Takes a domain you're checking for (e.g. an SSO/ADFS service you've identified)
- Follows redirects across every subdomain in `active_subdomains.txt` and reports any that ultimately land on the target domain
- Useful for identifying which discovered applications actually authenticate through a given identity provider, once one has been found via recon

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
# Enter the path to the program's scope CSV when prompted
```

```bash
python probe.py
# Choose "single" to probe one URL, or "all" to probe everything in worth_noting.txt
```

```bash
python trace.py
# Enter the domain you're checking redirects against, e.g. sso.example.com
# (requires active_subdomains.txt to already exist from a recon.py run)
```

## Scope and ethical use

This tool performs **passive reconnaissance only**:
- Certificate Transparency log queries (crt.sh) — public data, no interaction with the target at all
- Basic HTTP GET requests for liveness/header/redirect checks — equivalent to visiting a page in a browser

It does **not** perform active testing such as directory brute-forcing, parameter fuzzing, vulnerability scanning, or any form of exploitation.

The scope-filtering feature in `recon.py` is a deliberate safety measure: it ensures liveness checks and probing only ever touch assets a program has explicitly authorized, based on the program's own published scope data — not just assets that happen to resolve under a domain's certificate history.

Only run this against domains you own, or programs where you have explicit authorization (e.g., an enrolled bug bounty program operating within its defined scope). Passive recon of public data is generally low-risk, but you are responsible for confirming what's appropriate for your specific target and program rules.

## Project background

Built incrementally while learning Python and web recon fundamentals — this repo reflects an ongoing bug bounty learning journey rather than a finished, polished product. Future additions may include `robots.txt` / `sitemap.xml` / `security.txt` checking and concurrent request handling for faster scans.