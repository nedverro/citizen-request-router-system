# extract_organisations.py
# Objectif : récupérer toutes les organisations depuis l'API CKAN
# et les sauvegarder dans un fichier CSV

import requests
import pandas as pd

# ─────────────────────────────────────────
# ÉTAPE 1 : Récupérer la liste des slugs
# ─────────────────────────────────────────
print("Étape 1 : Récupération de la liste des organisations...")

url_liste = "https://data.gov.ma/data/api/3/action/organization_list"
response = requests.get(url_liste)
slugs = response.json()["result"]

print(f"→ {len(slugs)} organisations trouvées")

# ─────────────────────────────────────────
# ÉTAPE 2 : Récupérer les détails de chaque organisation
# ─────────────────────────────────────────
print("\nÉtape 2 : Récupération des détails...")

organisations = []

for slug in slugs:
    url_detail = "https://data.gov.ma/data/api/3/action/organization_show"
    res = requests.get(url_detail, params={"id": slug})
    data = res.json()

    if data["success"]:
        org = data["result"]
        organisations.append({
            "slug":        slug,
            "nom":         org.get("display_name", ""),
            "description": org.get("description", ""),
            "nb_datasets": org.get("package_count", 0)
        })
        print(f"  ✓ {slug}")

# ─────────────────────────────────────────
# ÉTAPE 3 : Sauvegarder en CSV
# ─────────────────────────────────────────
print("\nÉtape 3 : Sauvegarde...")

df = pd.DataFrame(organisations)
df.to_csv("organisations.csv", index=False, encoding="utf-8-sig")

print(f"\n✅ Terminé ! {len(df)} organisations sauvegardées dans organisations.csv")
print("\nAperçu :")
print(df[["slug", "nom", "nb_datasets"]].head(10))