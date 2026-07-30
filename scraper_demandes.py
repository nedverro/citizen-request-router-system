# scraper_demandes.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

print("Extraction des demandes e-participation...")

demandes = []
page = 1

while True:
    print(f"  → Page {page}...")
    
    url = f"https://data.gov.ma/fr/feedback?page={page}"
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Chercher les lignes de demandes
    items = soup.select("div.views-row")
    
    if not items:
        print("  → Plus de données, arrêt.")
        break
    
    for item in items:
        # Titre + lien
        titre_el = item.select_one("div.views-field-title a")
        titre = titre_el.text.strip() if titre_el else ""
        lien  = "https://data.gov.ma" + titre_el["href"] if titre_el else ""

        # Description
        body_el = item.select_one("div.views-field-body")
        description = body_el.text.strip() if body_el else ""

        demandes.append({
            "titre":       titre,
            "description": description,
            "url":         lien
        })
        print(f"    ✓ {titre[:60]}")
    
    page += 1
    time.sleep(1)

# Sauvegarder
df = pd.DataFrame(demandes)
df.to_csv("demandes.csv", index=False, encoding="utf-8-sig")
print(f"\n✅ {len(df)} demandes sauvegardées dans demandes.csv")
print(df.head())