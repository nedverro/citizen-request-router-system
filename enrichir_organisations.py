# enrichir_organisations.py
# Objectif : enrichir chaque organisation avec des mots-clés
# extraits des titres de ses datasets publiés sur data.gov.ma

import requests
import pandas as pd
import time

print("Chargement des organisations...")
df_orgs = pd.read_csv("organisations.csv")
print(f"→ {len(df_orgs)} organisations à enrichir")

# ─────────────────────────────────────────
# Fonction : récupérer les titres des datasets d'une organisation
# ─────────────────────────────────────────
def get_dataset_titles(slug):
    url = "https://data.gov.ma/data/api/3/action/package_search"
    params = {
        "fq": f"organization:{slug}",
        "rows": 50  # max 50 datasets par organisation
    }
    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    titres = []
    if data["success"]:
        for dataset in data["result"]["results"]:
            titres.append(dataset.get("title", ""))
    return titres

# ─────────────────────────────────────────
# Boucle principale : enrichir chaque organisation
# ─────────────────────────────────────────
mots_cles_par_org = []

for index, row in df_orgs.iterrows():
    slug = row["slug"]
    print(f"  → {slug}...")

    titres = get_dataset_titles(slug)

    # On joint tous les titres en un seul bloc de texte
    mots_cles = " | ".join(titres)
    mots_cles_par_org.append(mots_cles)

    time.sleep(0.5)  # pause pour ne pas surcharger l'API

# ─────────────────────────────────────────
# Ajouter la colonne au DataFrame
# ─────────────────────────────────────────
df_orgs["mots_cles_datasets"] = mots_cles_par_org

# ─────────────────────────────────────────
# Créer un profil texte complet (utilisé plus tard par le NLP)
# ─────────────────────────────────────────
df_orgs["profil_texte"] = (
    df_orgs["nom"].fillna("") + ". " +
    df_orgs["description"].fillna("") + ". " +
    df_orgs["mots_cles_datasets"].fillna("")
)

# ─────────────────────────────────────────
# Sauvegarder
# ─────────────────────────────────────────
df_orgs.to_csv("organisations_enriched.csv", index=False, encoding="utf-8-sig")
print(f"\n✅ Terminé ! organisations_enriched.csv créé avec {len(df_orgs)} organisations enrichies")
print("\nAperçu d'un profil enrichi :")
print(df_orgs.iloc[0]["profil_texte"][:300])