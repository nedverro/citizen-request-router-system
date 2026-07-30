# build_notifications.py
# Objectif : traiter toutes les demandes citoyennes,
# les router vers l'organisme pertinent,
# et sauvegarder les résultats dans une base SQLite
# (sans dupliquer les demandes déjà traitées)

import pandas as pd
import sqlite3
import os
from datetime import datetime

# Importer notre matcher hybride
from hybrid_matcher import matcher_hybride, decider

# ─────────────────────────────────────────
# ÉTAPE 1 : Créer la base de données SQLite
# ─────────────────────────────────────────
print("Initialisation de la base de données...")

conn = sqlite3.connect("notifications.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        titre            TEXT,
        url              TEXT UNIQUE,
        organisme_predit TEXT,
        nom_organisme    TEXT,
        score_confiance  REAL,
        decision         TEXT,
        statut           TEXT DEFAULT 'en_attente',
        date_creation    TEXT
    )
""")
conn.commit()
print("✅ Base de données prête !")

# ─────────────────────────────────────────
# ÉTAPE 2 : Charger les demandes
# ─────────────────────────────────────────
print("\nChargement des demandes...")
df_demandes = pd.read_csv("demandes.csv")
print(f"→ {len(df_demandes)} demandes dans le fichier")

# ─────────────────────────────────────────
# ÉTAPE 3 : Traiter chaque demande (en évitant les doublons)
# ─────────────────────────────────────────
print("\nTraitement des demandes...\n")

traites     = 0
ignores     = 0
auto_route  = 0
manuel      = 0

for index, row in df_demandes.iterrows():
    titre = str(row["titre"]).strip()
    url   = str(row["url"]).strip()

    if not titre or titre == "nan":
        continue

    # ─────────────────────────────────────
    # Vérifier si cette demande existe déjà (par son URL unique)
    # ─────────────────────────────────────
    cursor.execute("SELECT COUNT(*) FROM notifications WHERE url = ?", (url,))
    existe_deja = cursor.fetchone()[0] > 0

    if existe_deja:
        print(f"  ⏭ Déjà traité, ignoré : {titre[:50]}")
        ignores += 1
        continue

    # Construire le texte de la demande
    description = str(row.get("description", "")).strip()
    texte_demande = titre + " " + description

    # Matcher hybride
    resultats = matcher_hybride(texte_demande, top_k=3)
    decision  = decider(resultats)

    # Prendre le top-1
    top1 = resultats[0]

    # Sauvegarder dans la base
    cursor.execute("""
        INSERT INTO notifications 
        (titre, url, organisme_predit, nom_organisme, 
         score_confiance, decision, statut, date_creation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        titre,
        url,
        top1["slug"],
        top1["nom"],
        top1["score_final"],
        decision,
        "en_attente",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    traites += 1
    if decision == "auto_route":
        auto_route += 1
    else:
        manuel += 1

    print(f"  ✓ [{decision}] {titre[:50]} → {top1['nom']}")

conn.commit()
conn.close()

# ─────────────────────────────────────────
# ÉTAPE 4 : Résumé final
# ─────────────────────────────────────────
print(f"""
✅ Terminé !
───────────────────────────────
Nouvelles demandes traitées : {traites}
Demandes déjà existantes (ignorées) : {ignores}
Auto-route      : {auto_route}
Manuel review   : {manuel}
Base de données : notifications.db
""")