import os
import requests
import csv
from datetime import datetime

# Configurazione
REPO = "alessandroabbasciano-cpu/MoldForge"
TOKEN = os.environ.get("TRAFFIC_TOKEN")
CSV_FILE = "stats.csv"

if not TOKEN:
    print("Errore: TRAFFIC_TOKEN non trovato!")
    exit(1)

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Prende le Visualizzazioni (Views)
views_url = f"https://api.github.com/repos/{REPO}/traffic/views"
views_resp = requests.get(views_url, headers=headers).json()
views_count = views_resp.get("count", 0)
views_uniques = views_resp.get("uniques", 0)

# Prende i Cloni (Clones)
clones_url = f"https://api.github.com/repos/{REPO}/traffic/clones"
clones_resp = requests.get(clones_url, headers=headers).json()
clones_count = clones_resp.get("count", 0)
clones_uniques = clones_resp.get("uniques", 0)

# Data di oggi
date_today = datetime.now().strftime("%Y-%m-%d")

# Scrive nel CSV
file_exists = os.path.isfile(CSV_FILE)
with open(CSV_FILE, mode="a", newline="") as file:
    writer = csv.writer(file)
    # Se il file è nuovo, scrivi l'intestazione
    if not file_exists:
        writer.writerow(["Data", "Visualizzazioni Totali", "Visualizzazioni Uniche", "Cloni Totali", "Cloni Unici"])
    
    # Appende i dati
    writer.writerow([date_today, views_count, views_uniques, clones_count, clones_uniques])

print(f"Dati salvati per il {date_today}: Visite={views_count}, Cloni={clones_count}")