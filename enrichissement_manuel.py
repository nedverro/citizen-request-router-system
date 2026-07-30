# enrichissement_manuel.py
# Objectif : ajouter manuellement des mots-clés aux organisations
# qui ont un profil texte trop pauvre (moins de 50 mots)

import pandas as pd

# Dictionnaire d'enrichissement manuel
ENRICHISSEMENTS = {
    "region-beni-mellal-khenifra": 
        "région territoriale collectivité locale développement régional "
        "béni mellal khenifra province commune rural urbain",

    "fondation-nationale-des-musees": 
        "musée patrimoine culturel art histoire exposition collection "
        "archéologie monuments historiques culture nationale",

    "region-souss-massa": 
        "région souss massa agadir territoire collectivité locale "
        "développement régional province commune",

    "region-fes-meknes": 
        "région fès meknès territoire collectivité locale "
        "développement régional province commune patrimoine",

    "archives-du-maroc": 
        "archives documents historiques patrimoine documentaire "
        "conservation archives nationales mémoire institutionnelle",

    "ministere-de-l-equipement-et-de-l-eau": 
        "équipement infrastructure eau routes ponts barrages "
        "hydraulique ressources hydriques transport routier",

    "departement-de-l-agriculture": 
        "agriculture agricole terres cultivées irrigation céréales "
        "élevage rural développement agricole production alimentaire",

    "caisse-marocaine-des-retraites": 
        "retraite pension retraités fonctionnaires cotisation "
        "allocation vieillesse prévoyance sociale",

    "centre-regional-d-investissement-draa-tafilalet": 
        "investissement entreprise création activité économique "
        "draa tafilalet région développement économique",

    "ministere-des-affaires-etrangeres-et-de-la-cooperation": 
        "affaires étrangères diplomatie coopération internationale "
        "ambassade consulat relations extérieures traités"
}

# ─────────────────────────────────────────
# Charger le CSV enrichi
# ─────────────────────────────────────────
df = pd.read_csv("organisations_enriched.csv")

# ─────────────────────────────────────────
# Ajouter les mots-clés manuels
# ─────────────────────────────────────────
enrichies = 0
for index, row in df.iterrows():
    slug = row["slug"]
    if slug in ENRICHISSEMENTS:
        mots_supplementaires = ENRICHISSEMENTS[slug]
        df.at[index, "profil_texte"] = row["profil_texte"] + " " + mots_supplementaires
        enrichies += 1
        print(f"  ✓ Enrichi manuellement : {slug}")

# ─────────────────────────────────────────
# Sauvegarder
# ─────────────────────────────────────────
df.to_csv("organisations_enriched.csv", index=False, encoding="utf-8-sig")
print(f"\n✅ {enrichies} organisations enrichies manuellement")
print("Fichier organisations_enriched.csv mis à jour !")