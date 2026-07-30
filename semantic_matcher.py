# semantic_matcher.py
# Objectif : calculer le score sémantique entre une demande
# et les profils des organisations en utilisant des embeddings

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os

# ─────────────────────────────────────────
# ÉTAPE 1 : Charger les données
# ─────────────────────────────────────────
df_orgs = pd.read_csv("organisations_enriched.csv")
profils = df_orgs["profil_texte"].fillna("").tolist()
slugs   = df_orgs["slug"].tolist()
noms    = df_orgs["nom"].tolist()

# ─────────────────────────────────────────
# ÉTAPE 2 : Charger le modèle
# ─────────────────────────────────────────
print("Chargement du modèle sémantique...")
modele = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
print("✅ Modèle chargé !")

# ─────────────────────────────────────────
# ÉTAPE 3 : Calculer les embeddings des profils
# (on les sauvegarde pour ne pas recalculer à chaque fois)
# ─────────────────────────────────────────
FICHIER_EMBEDDINGS = "embeddings_orgs.pkl"

if os.path.exists(FICHIER_EMBEDDINGS):
    print("Chargement des embeddings existants...")
    with open(FICHIER_EMBEDDINGS, "rb") as f:
        embeddings_orgs = pickle.load(f)
else:
    print("Calcul des embeddings des organisations...")
    embeddings_orgs = modele.encode(profils, show_progress_bar=True)
    with open(FICHIER_EMBEDDINGS, "wb") as f:
        pickle.dump(embeddings_orgs, f)
    print("✅ Embeddings sauvegardés !")

# ─────────────────────────────────────────
# ÉTAPE 4 : Fonction de matching sémantique
# ─────────────────────────────────────────
def matcher_semantique(demande, top_k=3):
    # Calculer l'embedding de la demande
    embedding_demande = modele.encode([demande])
    
    # Calculer la similarité cosinus
    scores = cosine_similarity(embedding_demande, embeddings_orgs)[0]
    
    # Trier par score décroissant
    indices_tries = scores.argsort()[::-1][:top_k]
    
    resultats = []
    for i in indices_tries:
        resultats.append({
            "slug":  slugs[i],
            "nom":   noms[i],
            "score": round(float(scores[i]), 4)
        })
    
    return resultats

# ─────────────────────────────────────────
# ÉTAPE 5 : Tester avec les mêmes demandes
# ─────────────────────────────────────────
demandes_test = [
    "Je veux des données sur les télécommunications au Maroc",
    "Données sur les hôpitaux publics et la santé",
    "Statistiques sur l'agriculture et les céréales",
    "Informations sur les retraites et pensions"
]

print("\n=== TEST DU MATCHER SÉMANTIQUE ===\n")

for demande in demandes_test:
    print(f"Demande : {demande}")
    resultats = matcher_semantique(demande, top_k=3)
    for rang, r in enumerate(resultats, 1):
        print(f"  {rang}. {r['nom']} [{r['slug']}] → score: {r['score']}")
    print()