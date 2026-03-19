import os
import requests
import csv
from datetime import datetime

# Configuration
REPO = "alessandroabbasciano-cpu/MoldForge"
TOKEN = os.environ.get("TRAFFIC_TOKEN")
CSV_FILE = "traffic_stats.csv"

if not TOKEN:
    print("Error: TRAFFIC_TOKEN not found!")
    exit(1)

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Fetch Views
views_url = f"https://api.github.com/repos/{REPO}/traffic/views"
views_resp = requests.get(views_url, headers=headers).json()
views_uniques = views_resp.get("uniques", 0)

# Fetch Clones
clones_url = f"https://api.github.com/repos/{REPO}/traffic/clones"
clones_resp = requests.get(clones_url, headers=headers).json()
clones_uniques = clones_resp.get("uniques", 0)

# Today's date
date_today = datetime.now().strftime("%Y-%m-%d")

# Write to CSV
file_exists = os.path.isfile(CSV_FILE)
with open(CSV_FILE, mode="a", newline="") as file:
    writer = csv.writer(file)
    # Write header if file is new
    if not file_exists:
        writer.writerow(["Date", "Unique Views", "Unique Clones"])
    
    # Append raw unique data
    writer.writerow([date_today, views_uniques, clones_uniques])

print(f"Traffic data logged for {date_today} -> Unique Views: {views_uniques} | Unique Clones: {clones_uniques}")