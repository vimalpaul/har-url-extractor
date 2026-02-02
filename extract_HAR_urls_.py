import json
import sys
import os
from urllib.parse import urlparse
from openpyxl import Workbook
from collections import Counter

def extract_urls(har_file):
    with open(har_file, "r", encoding="utf-8", errors="ignore") as f:
        har = json.load(f)

    urls = []
    for entry in har.get("log", {}).get("entries", []):
        url = entry.get("request", {}).get("url")
        if url:
            urls.append(url)

    return sorted(set(urls))

def categorize(url):
    u = url.lower()
    if u.endswith(".js"):
        return "JS"
    if u.endswith(".css"):
        return "CSS"
    if any(x in u for x in [".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp"]):
        return "Images"
    if any(x in u for x in ["/api/", "api.", "graphql"]):
        return "APIs"
    if u.endswith("/") or ".html" in u:
        return "HTML"
    return "Other"

def save_excel(urls, output_file):
    wb = Workbook()
    ws = wb.active
    ws.title = "All Observed URLs"
    ws.append(["Category", "Domain", "URL"])

    counts = Counter()

    for url in urls:
        domain = urlparse(url).netloc
        category = categorize(url)
        ws.append([category, domain, url])
        counts[category] += 1

    wb.save(output_file)

    print("\n✅ URL list generated successfully")
    print(f"📁 Output file: {output_file}\n")
    print("Summary:")
    for k, v in counts.items():
        print(f"  {k}: {v}")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python extract_urls_list_only.py <har_file>")
        sys.exit(1)

    har_file = sys.argv[1]

    if not os.path.exists(har_file):
        print(f"❌ HAR file not found: {har_file}")
        sys.exit(1)

    urls = extract_urls(har_file)

    if not urls:
        print("⚠️ No URLs found in HAR. Check capture.")
        sys.exit(1)

    base_name = os.path.splitext(os.path.basename(har_file))[0]
    output_file = f"{base_name}_All_URLs.xlsx"

    save_excel(urls, output_file)

if __name__ == "__main__":
    main()
